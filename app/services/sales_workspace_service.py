from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    OpportunityStatus,
    Phase13AuditAction,
    Phase13DecisionValue,
    SalesWorkspaceRunOperation,
    SalesWorkspaceRunStatus,
    SalesWorkspaceStatus,
)
from app.db.models.campaign import Campaign
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase13_audit_event import Phase13AuditEvent
from app.db.models.phase13_decision import Phase13Decision
from app.db.models.sales_workspace_item import SalesWorkspaceItem
from app.db.models.sales_workspace_run import SalesWorkspaceRun
from app.services.human_only_action_guard_service import HumanOnlyActionGuardService
from app.services.internal_pricing_worksheet_service import InternalPricingWorksheetService
from app.services.manual_followup_plan_service import ManualFollowupPlanService
from app.services.next_human_action_service import NextHumanActionService
from app.services.opportunity_health_service import OpportunityHealthService
from app.services.proposal_checklist_service import ProposalChecklistService
from app.services.proposal_readiness_gate_service import ProposalReadinessGateService
from app.services.quote_readiness_gate_service import QuoteReadinessGateService
from app.services.sales_task_service import SalesTaskService
from app.services.scope_checklist_service import ScopeChecklistService
from app.services.scope_completeness_service import ScopeCompletenessService
from app.settings import Settings


class SalesWorkspaceService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def build_for_campaign(self, campaign_slug: str, commit: bool) -> dict:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        opportunities = self._active_opportunities(campaign.id)
        if not commit:
            return {
                "dry_run": True,
                "input_opportunity_count": len(opportunities),
                "workspace_item_count": 0,
                "tasks_created_count": 0,
                "checklists_created_count": 0,
                "run_id": None,
            }
        guard = HumanOnlyActionGuardService(self.settings)
        for action in guard.blocked_actions:
            if guard.check(action).allowed:
                run = self._run(campaign.id, True)
                run.status = SalesWorkspaceRunStatus.BLOCKED_BY_HUMAN_ONLY_GUARD_FAILURE
                return {
                    "dry_run": False,
                    "input_opportunity_count": len(opportunities),
                    "workspace_item_count": 0,
                    "tasks_created_count": 0,
                    "checklists_created_count": 0,
                    "run_id": run.run_id,
                }
        run = self._run(campaign.id, False)
        tasks_created = checklists_created = workspace_items = 0
        for opportunity in opportunities:
            item = self.create_item(opportunity)
            workspace_items += 1
            scope = ScopeChecklistService(self.session).create_for_opportunity(opportunity)
            ScopeCompletenessService(self.session, self.settings).calculate(scope)
            proposal = ProposalChecklistService(self.session).create_for_opportunity(opportunity)
            InternalPricingWorksheetService(self.session).create_for_opportunity(opportunity)
            ManualFollowupPlanService(self.session).create_for_opportunity(opportunity)
            tasks = SalesTaskService(self.session, self.settings).create_initial_tasks(opportunity)
            QuoteReadinessGateService(self.session).evaluate(opportunity.id)
            ProposalReadinessGateService(self.session, self.settings).evaluate(proposal)
            OpportunityHealthService(self.session).snapshot(opportunity)
            NextHumanActionService(self.session).create(opportunity)
            self.session.add(
                Phase13Decision(
                    opportunity_id=opportunity.id,
                    candidate_business_id=opportunity.candidate_business_id,
                    decision=Phase13DecisionValue.SALES_WORKSPACE_READY,
                    ready_for_phase14=False,
                    manual_action_required=True,
                    closed=False,
                    reason="Sales workspace ready for human-only operation.",
                )
            )
            self.session.add(
                Phase13AuditEvent(
                    opportunity_id=opportunity.id,
                    candidate_business_id=opportunity.candidate_business_id,
                    actor="system",
                    action=Phase13AuditAction.WORKSPACE_CREATED,
                    reason="Created Phase 13 workspace item; no outbound action performed.",
                )
            )
            checklists_created += 2 if scope and proposal else 0
            tasks_created += len(tasks)
            item.last_activity_at = datetime.now(UTC)
        run.input_opportunity_count = len(opportunities)
        run.workspace_item_count = workspace_items
        run.tasks_created_count = tasks_created
        run.checklists_created_count = checklists_created
        run.status = SalesWorkspaceRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        return {
            "dry_run": False,
            "input_opportunity_count": len(opportunities),
            "workspace_item_count": workspace_items,
            "tasks_created_count": tasks_created,
            "checklists_created_count": checklists_created,
            "run_id": run.run_id,
        }

    def create_item(self, opportunity: OpportunityRecord) -> SalesWorkspaceItem:
        existing = self.session.scalar(
            select(SalesWorkspaceItem).where(SalesWorkspaceItem.opportunity_id == opportunity.id)
        )
        if existing:
            return existing
        item = SalesWorkspaceItem(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            workspace_status=self._workspace_status(opportunity),
            priority=opportunity.priority,
        )
        self.session.add(item)
        self.session.flush()
        return item

    def _run(self, campaign_id: int, blocked: bool) -> SalesWorkspaceRun:
        run = SalesWorkspaceRun(
            run_id=f"phase13-{uuid4().hex[:10]}",
            campaign_id=campaign_id,
            operation=SalesWorkspaceRunOperation.PHASE13_FULL_WORKSPACE_BUILD,
            status=SalesWorkspaceRunStatus.BLOCKED_BY_HUMAN_ONLY_GUARD_FAILURE
            if blocked
            else SalesWorkspaceRunStatus.STARTED,
            dry_run=False,
            started_at=datetime.now(UTC),
        )
        self.session.add(run)
        self.session.flush()
        return run

    def _active_opportunities(self, campaign_id: int) -> list[OpportunityRecord]:
        rows = self.session.scalars(
            select(OpportunityRecord).where(OpportunityRecord.campaign_id == campaign_id)
        ).all()
        return [row for row in rows if not row.opportunity_status.name.startswith("CLOSED")]

    def _workspace_status(self, opportunity: OpportunityRecord) -> SalesWorkspaceStatus:
        if opportunity.opportunity_status == OpportunityStatus.ASKED_PRICE:
            return SalesWorkspaceStatus.WAITING_FOR_SCOPE
        if opportunity.opportunity_status == OpportunityStatus.CALL_REQUESTED:
            return SalesWorkspaceStatus.MANUAL_CALL_NEEDED
        if opportunity.opportunity_status == OpportunityStatus.ASKED_DETAILS:
            return SalesWorkspaceStatus.PROPOSAL_CHECKLIST_READY
        return SalesWorkspaceStatus.NEEDS_MANUAL_REPLY
