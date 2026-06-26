from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import OpportunityHealthStatus, OpportunityStatus, SalesTaskStatus
from app.db.models.opportunity_health_snapshot import OpportunityHealthSnapshot
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.proposal_checklist import ProposalChecklist
from app.db.models.sales_task import SalesTask
from app.db.models.scope_checklist import ScopeChecklist


class OpportunityHealthService:
    def __init__(self, session: Session):
        self.session = session

    def snapshot(self, opportunity: OpportunityRecord) -> OpportunityHealthSnapshot:
        scope = self.session.scalar(
            select(ScopeChecklist).where(ScopeChecklist.opportunity_id == opportunity.id)
        )
        proposal = self.session.scalar(
            select(ProposalChecklist).where(ProposalChecklist.opportunity_id == opportunity.id)
        )
        tasks = self.session.scalars(
            select(SalesTask).where(SalesTask.opportunity_id == opportunity.id)
        ).all()
        overdue = [
            task
            for task in tasks
            if task.status == SalesTaskStatus.OPEN and task.due_at and self._is_overdue(task.due_at)
        ]
        status = self._status(opportunity, scope.completeness_score if scope else 0, bool(overdue))
        snapshot = OpportunityHealthSnapshot(
            opportunity_id=opportunity.id,
            health_status=status,
            reply_quality_score=int(opportunity.confidence * 100),
            scope_completeness_score=scope.completeness_score if scope else 0,
            customer_intent_score=80
            if opportunity.opportunity_status
            in {OpportunityStatus.ASKED_PRICE, OpportunityStatus.CALL_REQUESTED}
            else 60,
            contact_reliability_score=70,
            proposal_readiness_score=proposal.readiness_score if proposal else 0,
            task_overdue_risk_score=100 if overdue else 0,
            notes_json={"human_only": True},
        )
        self.session.add(snapshot)
        return snapshot

    def _status(
        self, opportunity: OpportunityRecord, scope_score: int, overdue: bool
    ) -> OpportunityHealthStatus:
        if opportunity.opportunity_status.name.startswith("CLOSED"):
            return OpportunityHealthStatus.CLOSED
        if overdue:
            return OpportunityHealthStatus.AT_RISK_STALE
        if scope_score < 70:
            return OpportunityHealthStatus.NEEDS_SCOPE
        return OpportunityHealthStatus.HEALTHY

    def _is_overdue(self, due_at: datetime) -> bool:
        now = datetime.now(UTC)
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=UTC)
        return due_at < now
