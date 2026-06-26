import re
from html import unescape

from app.settings import Settings


class InboundPrivacyRedactionService:
    SECRET_PATTERNS = [
        re.compile(r"(?i)(password|api[_-]?key|token|secret)\s*[:=]\s*\S+"),
        re.compile(r"(?i)authorization:\s*\S+"),
    ]

    def __init__(self, settings: Settings):
        self.settings = settings

    def sanitize_text(self, value: str) -> str:
        text = unescape(value or "")
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", text)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?s)<[^>]+>", " ", text)
        for pattern in self.SECRET_PATTERNS:
            text = pattern.sub("[redacted]", text)
        text = re.sub(r"\s+\n", "\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text).strip()
        return text[: self.settings.inbound_max_body_chars]

    def safe_headers(self, headers: dict[str, str]) -> dict[str, str]:
        allowed = {
            "message-id",
            "in-reply-to",
            "references",
            "from",
            "to",
            "subject",
            "date",
            "x-a2-send-queue-id",
            "x-a2-candidate-id",
        }
        return {key: value for key, value in headers.items() if key.lower() in allowed}
