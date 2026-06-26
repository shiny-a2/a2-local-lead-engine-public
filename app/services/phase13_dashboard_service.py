from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.manual_communication_log import ManualCommunicationLog
from app.db.models.next_human_action import NextHumanAction
from app.db.models.opportunity_close_record import OpportunityCloseRecord
from app.db.models.opportunity_health_snapshot import OpportunityHealthSnapshot
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.proposal_checklist import ProposalChecklist
from app.db.models.sales_task import SalesTask
from app.db.models.sales_workspace_item import SalesWorkspaceItem
from app.db.models.scope_checklist import ScopeChecklist


class Phase13DashboardService:
    def __init__(self, session: Session):
        self.session = session

    def dashboard(self) -> dict:
        items = self.session.scalars(select(SalesWorkspaceItem)).all()
        tasks = self.session.scalars(select(SalesTask)).all()
        return {
            "workspace_items": len(items),
            "open_tasks": sum(1 for task in tasks if task.status.value == "OPEN"),
            "closed": len(self.session.scalars(select(OpportunityCloseRecord)).all()),
            "outbound_actions": False,
        }

    def detail(self, opportunity_id: int) -> dict:
        opportunity = self.session.get(OpportunityRecord, opportunity_id)
        return {
            "opportunity": opportunity,
            "workspace": self.session.scalar(
                select(SalesWorkspaceItem).where(SalesWorkspaceItem.opportunity_id == opportunity_id)
            ),
            "scope": self.session.scalar(
                select(ScopeChecklist).where(ScopeChecklist.opportunity_id == opportunity_id)
            ),
            "proposal": self.session.scalar(
                select(ProposalChecklist).where(ProposalChecklist.opportunity_id == opportunity_id)
            ),
            "health": self.session.scalars(
                select(OpportunityHealthSnapshot).where(
                    OpportunityHealthSnapshot.opportunity_id == opportunity_id
                )
            ).all(),
            "tasks": self.session.scalars(
                select(SalesTask).where(SalesTask.opportunity_id == opportunity_id)
            ).all(),
            "next_actions": self.session.scalars(
                select(NextHumanAction).where(NextHumanAction.opportunity_id == opportunity_id)
            ).all(),
            "logs": self.session.scalars(
                select(ManualCommunicationLog).where(
                    ManualCommunicationLog.opportunity_id == opportunity_id
                )
            ).all(),
        }
