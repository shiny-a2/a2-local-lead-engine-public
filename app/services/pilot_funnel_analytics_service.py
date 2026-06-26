from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.candidate_business import CandidateBusiness
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.pilot_batch_candidate import PilotBatchCandidate


class PilotFunnelAnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    def snapshot(self, campaign_id: int) -> dict[str, int]:
        return {
            "candidates": self._count(CandidateBusiness),
            "pilot_batch_candidates": self._count(PilotBatchCandidate),
            "draft_variants": self._count(EmailDraftVariant),
            "send_queue_items": self._count(EmailSendQueue),
            "sent_to_provider": sum(
                1
                for row in self.session.scalars(select(EmailSendQueue)).all()
                if row.queue_status.value == "SENT_TO_PROVIDER"
            ),
            "inbound_messages": self._count(InboundEmailMessage),
            "opportunities": self._count(OpportunityRecord),
        }

    def _count(self, model: type) -> int:
        return len(self.session.scalars(select(model)).all())
