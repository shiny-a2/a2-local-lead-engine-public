from email.message import EmailMessage

from app.core.enums import EmailProviderType, ProviderStatus
from app.services.email_provider_base import ProviderResult


class NullDryRunProvider:
    provider_type = EmailProviderType.NULL_DRY_RUN

    def check_config(self) -> tuple[bool, list[str]]:
        return True, ["null_dry_run_provider_ready"]

    def send(self, message: EmailMessage, dry_run: bool) -> ProviderResult:
        return ProviderResult(
            provider_type=self.provider_type,
            provider_status=ProviderStatus.DRY_RUN,
            provider_message_id="dry-run",
        )

    def supports_delivery_events(self) -> bool:
        return False

    def supports_webhooks(self) -> bool:
        return False

    def supports_custom_headers(self) -> bool:
        return True
