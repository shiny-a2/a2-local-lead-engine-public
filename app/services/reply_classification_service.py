from sqlalchemy.orm import Session

from app.core.enums import InboundMessageType, ReplyClassificationValue, ReplyClassifierType
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.reply_classification import ReplyClassification
from app.settings import Settings


class ReplyClassificationService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def classify_text(self, subject: str, body: str) -> tuple[ReplyClassificationValue, float, list[str]]:
        text = f"{subject}\n{body}".lower()
        if any(word in text for word in ["unsubscribe", "remove me", "stop emailing"]):
            return ReplyClassificationValue.UNSUBSCRIBE_REQUEST, 0.95, ["unsubscribe_request"]
        if any(word in text for word in ["out of office", "automatic reply", "auto-reply"]):
            return ReplyClassificationValue.OUT_OF_OFFICE, 0.92, ["auto_reply"]
        if any(word in text for word in ["delivery status notification", "undeliver", "bounce"]):
            return ReplyClassificationValue.BOUNCE_LIKE, 0.9, ["bounce_like"]
        if any(word in text for word in ["price", "cost", "how much", "pricing"]):
            return ReplyClassificationValue.ASKING_PRICE, 0.82, ["price_request"]
        if any(word in text for word in ["details", "tell me more", "more info"]):
            return ReplyClassificationValue.ASKING_DETAILS, 0.78, ["details_request"]
        if any(word in text for word in ["call me", "phone me", "give me a call"]):
            return ReplyClassificationValue.REQUESTED_CALL, 0.8, ["call_request"]
        if any(word in text for word in ["not interested", "no thanks", "no thank you"]):
            return ReplyClassificationValue.NOT_INTERESTED, 0.86, ["negative_reply"]
        if "already have" in text and "website" in text:
            return ReplyClassificationValue.ALREADY_HAS_WEBSITE, 0.82, ["already_has_website"]
        if any(word in text for word in ["wrong person", "wrong contact", "not me"]):
            return ReplyClassificationValue.WRONG_CONTACT, 0.82, ["wrong_contact"]
        if any(word in text for word in ["interested", "sounds good", "yes", "sure"]):
            return ReplyClassificationValue.POSITIVE_INTEREST, 0.75, ["positive_interest"]
        return ReplyClassificationValue.UNKNOWN_NEEDS_REVIEW, 0.3, ["low_confidence"]

    def classify(self, message: InboundEmailMessage) -> ReplyClassification:
        classification, confidence, signals = self.classify_text(
            message.subject, message.body_text_sanitized
        )
        if classification == ReplyClassificationValue.UNSUBSCRIBE_REQUEST:
            message.message_type = InboundMessageType.UNSUBSCRIBE_REQUEST
        elif classification in {
            ReplyClassificationValue.AUTO_REPLY,
            ReplyClassificationValue.OUT_OF_OFFICE,
        }:
            message.message_type = InboundMessageType.OUT_OF_OFFICE
        elif classification == ReplyClassificationValue.BOUNCE_LIKE:
            message.message_type = InboundMessageType.BOUNCE
        elif message.message_type == InboundMessageType.UNKNOWN:
            message.message_type = InboundMessageType.REPLY
        row = ReplyClassification(
            inbound_message_id=message.id,
            candidate_business_id=message.matched_candidate_business_id,
            classification=classification,
            confidence=confidence,
            classifier_type=ReplyClassifierType.RULE_BASED,
            signals_json={"signals": signals, "ai_used": False},
        )
        self.session.add(row)
        self.session.flush()
        return row
