import smtplib
from email.message import EmailMessage

from app.core.enums import EmailProviderType, ProviderStatus
from app.services.email_provider_base import ProviderResult
from app.settings import Settings


class CpanelSmtpProvider:
    provider_type = EmailProviderType.CPANEL_SMTP

    def __init__(self, settings: Settings, smtp_factory=None):
        self.settings = settings
        self.smtp_factory = smtp_factory or smtplib.SMTP

    def check_config(self) -> tuple[bool, list[str]]:
        missing = []
        for key, value in {
            "SMTP_HOST": self.settings.smtp_host,
            "SMTP_USERNAME": self.settings.smtp_username,
            "SMTP_PASSWORD": self.settings.smtp_password,
            "FROM_EMAIL": self.settings.default_from_email or self.settings.smtp_from_email,
        }.items():
            if not value:
                missing.append(f"{key}_MISSING")
        return not missing, missing or ["cpanel_smtp_config_present"]

    def send(self, message: EmailMessage, dry_run: bool) -> ProviderResult:
        if dry_run:
            return ProviderResult(self.provider_type, ProviderStatus.DRY_RUN, "dry-run")
        ok, gaps = self.check_config()
        if not ok:
            return ProviderResult(
                self.provider_type,
                ProviderStatus.BLOCKED,
                error_type="CONFIG_MISSING",
                error_message=";".join(gaps),
                permanent_error=True,
            )
        try:
            with self.smtp_factory(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as smtp:
                if self.settings.smtp_use_tls:
                    smtp.starttls()
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
                response = smtp.send_message(message)
            return ProviderResult(
                self.provider_type,
                ProviderStatus.ACCEPTED,
                provider_message_id=message.get("Message-ID"),
                smtp_response_code="250" if not response else "partial",
            )
        except smtplib.SMTPException as exc:
            return ProviderResult(
                self.provider_type,
                ProviderStatus.FAILED,
                error_type=exc.__class__.__name__,
                error_message=str(exc)[:500],
                transient_error=True,
            )

    def supports_delivery_events(self) -> bool:
        return False

    def supports_webhooks(self) -> bool:
        return False

    def supports_custom_headers(self) -> bool:
        return True
