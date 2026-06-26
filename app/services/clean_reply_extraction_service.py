import hashlib
import re

from sqlalchemy.orm import Session

from app.core.enums import InboundPartType
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.inbound_message_part import InboundMessagePart


class CleanReplyExtractionService:
    QUOTE_PATTERNS = [r"(?im)^On .+ wrote:$", r"(?im)^From:\s", r"(?im)^>"]
    SIGNATURE_PATTERN = re.compile(
        r"^--\s*$|^kind regards,|^thanks,", re.MULTILINE | re.IGNORECASE
    )

    def __init__(self, session: Session):
        self.session = session

    def extract(self, message: InboundEmailMessage) -> tuple[str, float]:
        text = message.body_text_sanitized
        quote_at = len(text)
        for pattern in self.QUOTE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                quote_at = min(quote_at, match.start())
        clean = text[:quote_at].strip()
        quoted = text[quote_at:].strip()
        signature = ""
        sig_match = self.SIGNATURE_PATTERN.search(clean)
        if sig_match:
            signature = clean[sig_match.start() :].strip()
            clean = clean[: sig_match.start()].strip()
        confidence = 0.9 if clean else 0.3
        self._part(message.id, InboundPartType.CLEAN_REPLY, clean, confidence)
        if quoted:
            self._part(message.id, InboundPartType.QUOTED_PREVIOUS_THREAD, quoted, 0.8)
        if signature:
            self._part(message.id, InboundPartType.SIGNATURE, signature, 0.7)
        self.session.flush()
        return clean, confidence

    def _part(self, message_id: int, part_type: InboundPartType, content: str, confidence: float) -> None:
        self.session.add(
            InboundMessagePart(
                inbound_message_id=message_id,
                part_type=part_type,
                content_text=content,
                content_hash=hashlib.sha256(content.encode()).hexdigest(),
                confidence=confidence,
            )
        )
