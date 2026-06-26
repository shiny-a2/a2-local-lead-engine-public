from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

from app.core.enums import EmailProviderType, ProviderStatus


@dataclass(frozen=True)
class ProviderResult:
    provider_type: EmailProviderType
    provider_status: ProviderStatus
    provider_message_id: str | None = None
    smtp_response_code: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    transient_error: bool = False
    permanent_error: bool = False


class EmailProviderBase(Protocol):
    provider_type: EmailProviderType

    def check_config(self) -> tuple[bool, list[str]]:
        ...

    def send(self, message: EmailMessage, dry_run: bool) -> ProviderResult:
        ...

    def supports_delivery_events(self) -> bool:
        return False

    def supports_webhooks(self) -> bool:
        return False

    def supports_custom_headers(self) -> bool:
        return True
