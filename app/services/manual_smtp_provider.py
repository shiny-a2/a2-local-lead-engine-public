from email.message import EmailMessage

from app.core.enums import EmailProviderType, ProviderStatus
from app.services.email_provider_base import ProviderResult


class ManualSmtpProvider:
    provider_type = EmailProviderType.MANUAL_SMTP

    def check_config(self) -> tuple[bool, list[str]]:
        return False, ["manual_smtp_is_placeholder_no_automatic_send"]

    def send(self, message: EmailMessage, dry_run: bool) -> ProviderResult:
        return ProviderResult(
            self.provider_type,
            ProviderStatus.BLOCKED,
            error_type="MANUAL_PROVIDER_PLACEHOLDER",
            error_message="Manual SMTP does not send automatically in Phase 10.",
            permanent_error=True,
        )
