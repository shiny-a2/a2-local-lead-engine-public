from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    LeadResponseLatestStatus,
    LeadResponseTimelineEventType,
    ReplyClassificationValue,
)
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.lead_response_status import LeadResponseStatus
from app.db.models.lead_response_timeline import LeadResponseTimeline
from app.db.models.reply_classification import ReplyClassification


class LeadResponseStatusService:
    def __init__(self, session: Session):
        self.session = session

    def status_for(self, classification: ReplyClassificationValue) -> LeadResponseLatestStatus:
        mapping = {
            ReplyClassificationValue.POSITIVE_INTEREST: LeadResponseLatestStatus.REPLIED_POSITIVE,
            ReplyClassificationValue.ASKING_PRICE: LeadResponseLatestStatus.ASKED_FOR_PRICE,
            ReplyClassificationValue.ASKING_DETAILS: LeadResponseLatestStatus.ASKED_FOR_DETAILS,
            ReplyClassificationValue.REQUESTED_CALL: LeadResponseLatestStatus.CALL_REQUESTED,
            ReplyClassificationValue.NOT_INTERESTED: LeadResponseLatestStatus.CLOSED_NOT_INTERESTED,
            ReplyClassificationValue.ALREADY_HAS_WEBSITE: LeadResponseLatestStatus.REPLIED_NEUTRAL,
            ReplyClassificationValue.WRONG_CONTACT: LeadResponseLatestStatus.WRONG_CONTACT,
            ReplyClassificationValue.UNSUBSCRIBE_REQUEST: LeadResponseLatestStatus.UNSUBSCRIBED,
            ReplyClassificationValue.OUT_OF_OFFICE: LeadResponseLatestStatus.AUTO_REPLY_ONLY,
            ReplyClassificationValue.AUTO_REPLY: LeadResponseLatestStatus.AUTO_REPLY_ONLY,
            ReplyClassificationValue.BOUNCE_LIKE: LeadResponseLatestStatus.BOUNCED_SOFT,
        }
        return mapping.get(classification, LeadResponseLatestStatus.NEEDS_HUMAN_ACTION)

    def update(
        self,
        message: InboundEmailMessage,
        classification: ReplyClassification,
        campaign_id: int,
    ) -> LeadResponseStatus | None:
        if message.matched_candidate_business_id is None:
            return None
        latest = self.status_for(classification.classification)
        human = latest in {
            LeadResponseLatestStatus.REPLIED_POSITIVE,
            LeadResponseLatestStatus.ASKED_FOR_PRICE,
            LeadResponseLatestStatus.ASKED_FOR_DETAILS,
            LeadResponseLatestStatus.CALL_REQUESTED,
            LeadResponseLatestStatus.NEEDS_HUMAN_ACTION,
        }
        row = self.session.scalar(
            select(LeadResponseStatus).where(
                LeadResponseStatus.candidate_business_id == message.matched_candidate_business_id
            )
        )
        if row is None:
            row = LeadResponseStatus(
                candidate_business_id=message.matched_candidate_business_id,
                campaign_id=campaign_id,
                latest_status=latest,
                status_reason=classification.classification.value,
            )
            self.session.add(row)
        row.latest_status = latest
        row.latest_inbound_message_id = message.id
        row.latest_send_queue_id = message.matched_send_queue_id
        row.human_action_required = human
        row.closed = latest in {
            LeadResponseLatestStatus.CLOSED_NOT_INTERESTED,
            LeadResponseLatestStatus.UNSUBSCRIBED,
            LeadResponseLatestStatus.WRONG_CONTACT,
        }
        row.status_reason = classification.classification.value
        self.session.add(
            LeadResponseTimeline(
                candidate_business_id=message.matched_candidate_business_id,
                event_type=LeadResponseTimelineEventType.STATUS_CHANGED,
                event_source="phase11",
                event_summary=f"Status updated to {latest.value}",
                related_send_queue_id=message.matched_send_queue_id,
                related_inbound_message_id=message.id,
                metadata_json={"classification": classification.classification.value},
            )
        )
        return row
