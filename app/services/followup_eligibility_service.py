from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.enums import FollowupType, OpportunityStatus
from app.db.models.followup_eligibility_record import FollowupEligibilityRecord
from app.db.models.opportunity_record import OpportunityRecord
from app.settings import Settings


class FollowupEligibilityService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create(self, opportunity: OpportunityRecord) -> FollowupEligibilityRecord:
        actionable = opportunity.opportunity_status in {
            OpportunityStatus.QUALIFIED_INTEREST,
            OpportunityStatus.ASKED_PRICE,
            OpportunityStatus.ASKED_DETAILS,
            OpportunityStatus.CALL_REQUESTED,
        }
        row = FollowupEligibilityRecord(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            inbound_message_id=opportunity.source_inbound_message_id,
            eligible=actionable,
            followup_type=FollowupType.MANUAL_ONLY if actionable else FollowupType.NOT_ALLOWED,
            reason="Manual-only follow-up planning; no automatic follow-up is allowed.",
            not_before=datetime.now(UTC)
            + timedelta(days=self.settings.phase12_followup_default_delay_days)
            if actionable
            else None,
            blocked_reason=None if actionable else "negative, unsubscribe, bounce, or non-actionable reply",
        )
        self.session.add(row)
        self.session.flush()
        return row
