from sqlalchemy.orm import Session

from app.core.enums import BounceSource, BounceType, InboundMessageType
from app.db.models.bounce_event import BounceEvent
from app.db.models.inbound_email_message import InboundEmailMessage


class BounceDetectionService:
    HARD = ["user unknown", "recipient address rejected", "no such user", "invalid recipient"]
    SOFT = ["mailbox full", "temporarily deferred", "try again later", "temporary failure"]

    def __init__(self, session: Session):
        self.session = session

    def detect_type(self, subject: str, body: str) -> tuple[bool, BounceType, str]:
        text = f"{subject}\n{body}".lower()
        if "delivery status notification" not in text and "undeliver" not in text and "bounce" not in text:
            return False, BounceType.UNKNOWN_BOUNCE, "not_bounce"
        for needle in self.HARD:
            if needle in text:
                return True, BounceType.HARD_BOUNCE, needle
        for needle in self.SOFT:
            if needle in text:
                return True, BounceType.SOFT_BOUNCE, needle
        return True, BounceType.UNKNOWN_BOUNCE, "unknown bounce"

    def create_event(self, message: InboundEmailMessage) -> BounceEvent | None:
        is_bounce, bounce_type, reason = self.detect_type(
            message.subject, message.body_text_sanitized
        )
        if not is_bounce:
            return None
        message.message_type = InboundMessageType.BOUNCE
        event = BounceEvent(
            inbound_message_id=message.id,
            email_send_queue_id=message.matched_send_queue_id,
            candidate_business_id=message.matched_candidate_business_id,
            recipient_email=message.from_email,
            bounce_source=BounceSource.IMAP_DSN,
            bounce_type=bounce_type,
            bounce_reason=reason,
            diagnostic_text=message.body_text_sanitized[:1000],
            manual_review_required=bounce_type == BounceType.UNKNOWN_BOUNCE,
        )
        self.session.add(event)
        self.session.flush()
        return event
