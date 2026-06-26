from sqlalchemy.orm import Session

from app.core.enums import ManualCommunicationChannel, ManualCommunicationType, Phase13AuditAction
from app.db.models.manual_communication_log import ManualCommunicationLog
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase13_audit_event import Phase13AuditEvent


class ManualCommunicationLogService:
    def __init__(self, session: Session):
        self.session = session

    def log(
        self,
        opportunity: OpportunityRecord,
        communication_type: ManualCommunicationType,
        summary: str,
        created_by: str,
        channel: ManualCommunicationChannel = ManualCommunicationChannel.MANUAL_NOTE,
    ) -> ManualCommunicationLog:
        log = ManualCommunicationLog(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            communication_type=communication_type,
            channel=channel,
            summary=summary,
            sent_by_human=True,
            created_by=created_by,
        )
        self.session.add(log)
        self.session.add(
            Phase13AuditEvent(
                opportunity_id=opportunity.id,
                candidate_business_id=opportunity.candidate_business_id,
                actor=created_by,
                action=Phase13AuditAction.MANUAL_COMMUNICATION_LOGGED,
                reason="Logged human action performed outside the system.",
            )
        )
        return log
