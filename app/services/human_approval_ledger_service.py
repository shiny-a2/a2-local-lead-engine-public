from sqlalchemy.orm import Session

from app.core.enums import HumanApprovalType, Phase13AuditAction
from app.db.models.human_approval_ledger import HumanApprovalLedger
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase13_audit_event import Phase13AuditEvent


class HumanApprovalLedgerService:
    def __init__(self, session: Session):
        self.session = session

    def record(
        self,
        opportunity: OpportunityRecord,
        approval_type: HumanApprovalType,
        approved_by: str,
        notes: str = "",
    ) -> HumanApprovalLedger:
        if not approved_by:
            raise ValueError("approved_by is required")
        ledger = HumanApprovalLedger(
            opportunity_id=opportunity.id,
            approval_type=approval_type,
            approved_by=approved_by,
            notes=notes,
        )
        self.session.add(ledger)
        self.session.add(
            Phase13AuditEvent(
                opportunity_id=opportunity.id,
                candidate_business_id=opportunity.candidate_business_id,
                actor=approved_by,
                action=Phase13AuditAction.QUOTE_APPROVED_MANUALLY
                if approval_type == HumanApprovalType.MANUAL_QUOTE_APPROVAL
                else Phase13AuditAction.PROPOSAL_ITEM_UPDATED,
                reason="Human approval recorded for internal workflow only.",
            )
        )
        return ledger
