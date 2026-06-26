from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    BounceType,
    InboundAuditAction,
    ReplyClassificationValue,
    SuppressionReason,
)
from app.db.models.bounce_event import BounceEvent
from app.db.models.inbound_audit_event import InboundAuditEvent
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.reply_classification import ReplyClassification
from app.db.models.suppression import SuppressionList
from app.settings import Settings


class SuppressionFromInboundService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def apply_for_bounce(self, bounce: BounceEvent) -> bool:
        if not self.settings.auto_suppress_hard_bounces:
            return False
        if bounce.bounce_type != BounceType.HARD_BOUNCE:
            return False
        self._suppress(bounce.recipient_email, SuppressionReason.BOUNCED, "hard bounce")
        bounce.suppression_applied = True
        return True

    def apply_for_reply(
        self, message: InboundEmailMessage, classification: ReplyClassification
    ) -> bool:
        if (
            classification.classification == ReplyClassificationValue.UNSUBSCRIBE_REQUEST
            and self.settings.auto_suppress_unsubscribe_requests
        ):
            self._suppress(message.from_email, SuppressionReason.UNSUBSCRIBED, "unsubscribe reply")
            self._audit(message, "unsubscribe reply suppression")
            return True
        if (
            classification.classification == ReplyClassificationValue.NOT_INTERESTED
            and self.settings.auto_suppress_negative_replies
        ):
            self._suppress(message.from_email, SuppressionReason.MANUAL_BLOCK, "negative reply")
            self._audit(message, "negative reply suppression")
            return True
        return False

    def _suppress(self, email: str, reason: SuppressionReason, source: str) -> None:
        existing = self.session.scalar(
            select(SuppressionList).where(SuppressionList.email == email.lower())
        )
        if existing:
            return
        self.session.add(
            SuppressionList(email=email.lower(), reason=reason, source=f"inbound:{source}")
        )

    def _audit(self, message: InboundEmailMessage, reason: str) -> None:
        self.session.add(
            InboundAuditEvent(
                inbound_message_id=message.id,
                candidate_business_id=message.matched_candidate_business_id,
                actor="system",
                action=InboundAuditAction.SUPPRESSION_APPLIED,
                reason=reason,
            )
        )
