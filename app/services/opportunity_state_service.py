from sqlalchemy.orm import Session

from app.core.enums import OpportunityStatus, SalesWorkspaceStatus
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.sales_workspace_item import SalesWorkspaceItem


class OpportunityStateService:
    def __init__(self, session: Session):
        self.session = session

    def mark_waiting_for_scope(self, opportunity: OpportunityRecord) -> None:
        opportunity.opportunity_status = OpportunityStatus.AWAITING_HUMAN_ACTION
        item = self.session.query(SalesWorkspaceItem).filter_by(opportunity_id=opportunity.id).one_or_none()
        if item:
            item.workspace_status = SalesWorkspaceStatus.WAITING_FOR_SCOPE
