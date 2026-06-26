import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email import policy
from email.message import Message
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime

from app.services.inbound_privacy_redaction_service import InboundPrivacyRedactionService
from app.settings import Settings


@dataclass
class ParsedInboundMessage:
    message_uid: str | None
    message_id_header: str | None
    in_reply_to_header: str | None
    references_header: str | None
    from_email: str
    from_name: str | None
    to_email: str | None
    subject: str
    received_at: datetime
    raw_headers_json: dict[str, str]
    body_text_sanitized: str
    body_hash: str
    attachments: list[dict] = field(default_factory=list)


class InboundMessageParserService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redactor = InboundPrivacyRedactionService(settings)

    def parse_bytes(self, raw: bytes, uid: str | None = None) -> ParsedInboundMessage:
        message = BytesParser(policy=policy.default).parsebytes(raw)
        return self.parse_message(message, uid)

    def parse_message(self, message: Message, uid: str | None = None) -> ParsedInboundMessage:
        headers = {key: str(value) for key, value in message.items()}
        from_name, from_email = parseaddr(headers.get("From", ""))
        _, to_email = parseaddr(headers.get("To", ""))
        received_at = self._date(headers.get("Date"))
        body, attachments = self._extract_body(message)
        sanitized = self.redactor.sanitize_text(body)
        return ParsedInboundMessage(
            message_uid=uid,
            message_id_header=headers.get("Message-ID"),
            in_reply_to_header=headers.get("In-Reply-To"),
            references_header=headers.get("References"),
            from_email=from_email.lower(),
            from_name=from_name or None,
            to_email=to_email.lower() or None,
            subject=headers.get("Subject", ""),
            received_at=received_at,
            raw_headers_json=self.redactor.safe_headers(headers),
            body_text_sanitized=sanitized,
            body_hash=hashlib.sha256(sanitized.encode()).hexdigest(),
            attachments=attachments,
        )

    def duplicate_key(self, parsed: ParsedInboundMessage) -> str:
        key = parsed.message_id_header or f"{parsed.from_email}:{parsed.subject}:{parsed.body_hash}"
        return hashlib.sha256(key.encode()).hexdigest()

    def _date(self, value: str | None) -> datetime:
        if not value:
            return datetime.now(UTC)
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return datetime.now(UTC)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)

    def _extract_body(self, message: Message) -> tuple[str, list[dict]]:
        bodies: list[str] = []
        attachments: list[dict] = []
        for part in message.walk() if message.is_multipart() else [message]:
            disposition = (part.get_content_disposition() or "").lower()
            filename = part.get_filename()
            content_type = part.get_content_type()
            if filename or disposition == "attachment":
                payload = part.get_payload(decode=True) or b""
                attachments.append(
                    {
                        "filename": filename or "attachment",
                        "mime_type": content_type,
                        "size_bytes": len(payload),
                        "stored": False,
                        "blocked_reason": "metadata_only_phase11",
                    }
                )
                continue
            if content_type in {"text/plain", "text/html"}:
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    payload_text = payload.decode(
                        part.get_content_charset() or "utf-8", "replace"
                    )
                else:
                    payload_text = str(part.get_payload())
                bodies.append(payload_text)
        return "\n".join(bodies), attachments
