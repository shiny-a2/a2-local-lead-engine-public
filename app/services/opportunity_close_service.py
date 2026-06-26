from sqlalchemy.orm import Session

from app.core.enums import (
    HumanApprovalType,
    OpportunityCloseReason,
    OpportunityStatus,
    Phase13AuditAction,
    SalesWorkspaceStatus,
)
from app.db.models.opportunity_close_record import OpportunityCloseRecord
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase13_audit_event import Phase13AuditEvent
from app.db.models.sales_workspace_item import SalesWorkspaceItem
from app.services.human_approval_ledger_service import HumanApprovalLedgerService


class OpportunityCloseService:
    def __init__(self, session: Session):
        self.session = session

    def close(
        self,
        opportunity: OpportunityRecord,
        close_reason: OpportunityCloseReason,
        closed_by: str,
        notes: str = "",
    ) -> OpportunityCloseRecord:
        if not close_reason or not closed_by:
            raise ValueError("close reason and closed_by are required")
        record = OpportunityCloseRecord(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            close_reason=close_reason,
            closed_by=closed_by,
            notes=notes,
        )
        opportunity.opportunity_status = self._status(close_reason)
        item = self.session.query(SalesWorkspaceItem).filter_by(opportunity_id=opportunity.id).one_or_none()
        if item:
            item.workspace_status = self._workspace_status(close_reason)
        self.session.add(record)
        HumanApprovalLedgerService(self.session).record(
            opportunity, HumanApprovalType.OPPORTUNITY_CLOSE_DECISION, closed_by, notes
        )
        self.session.add(
            Phase13AuditEvent(
                opportunity_id=opportunity.id,
                candidate_business_id=opportunity.candidate_business_id,
                actor=closed_by,
                action=Phase13AuditAction.OPPORTUNITY_CLOSED,
                reason=close_reason.value,
            )
        )
        self.session.flush()
        return record

    def _status(self, close_reason: OpportunityCloseReason) -> OpportunityStatus:
        if close_reason == OpportunityCloseReason.WRONG_CONTACT:
            return OpportunityStatus.CLOSED_WRONG_CONTACT
        return OpportunityStatus.CLOSED_NOT_INTERESTED

    def _workspace_status(self, close_reason: OpportunityCloseReason) -> SalesWorkspaceStatus:
        if close_reason == OpportunityCloseReason.WRONG_CONTACT:
            return SalesWorkspaceStatus.CLOSED_WRONG_CONTACT
        if close_reason == OpportunityCloseReason.NO_RESPONSE:
            return SalesWorkspaceStatus.CLOSED_NO_RESPONSE
        if close_reason == OpportunityCloseReason.WON:
            return SalesWorkspaceStatus.CLOSED_WON
        return SalesWorkspaceStatus.CLOSED_LOST
