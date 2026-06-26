from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import EmailProviderType, SenderProviderConfigStatus, SendWarmupStage
from app.db.models.sender_provider_config import SenderProviderConfig
from app.settings import Settings


class ProviderReadinessService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def ensure_default(self) -> SenderProviderConfig:
        row = self.session.scalar(
            select(SenderProviderConfig).where(
                SenderProviderConfig.provider_slug == self.settings.email_provider_slug
            )
        )
        if row:
            return row
        from_email = self.settings.default_from_email or self.settings.smtp_from_email
        reply_to = self.settings.default_reply_to_email or self.settings.smtp_reply_to or from_email
        domain = from_email.split("@")[-1] if "@" in from_email else ""
        row = SenderProviderConfig(
            provider_slug=self.settings.email_provider_slug,
            provider_type=EmailProviderType(self.settings.email_provider),
            from_email=from_email,
            from_name=self.settings.default_from_name or self.settings.smtp_from_name,
            reply_to_email=reply_to,
            domain=domain,
            status=SenderProviderConfigStatus.READY if from_email and reply_to else SenderProviderConfigStatus.NEEDS_REVIEW,
            daily_limit=self.settings.send_daily_limit,
            per_run_limit=self.settings.send_per_run_limit,
            per_domain_daily_limit=self.settings.send_per_domain_daily_limit,
            warmup_mode=self.settings.send_warmup_mode,
            warmup_stage=SendWarmupStage(self.settings.send_warmup_stage),
            spf_status="unknown",
            dkim_status="unknown",
            dmarc_status="unknown",
            reply_to_status="manual_ok" if reply_to else "needs_review",
            bounce_handling_mode=self.settings.cpanel_bounce_mode,
            notes_json=["No SMTP secrets are stored in DB."],
        )
        self.session.add(row)
        self.session.flush()
        return row

    def check(self) -> tuple[bool, list[str], SenderProviderConfig]:
        row = self.ensure_default()
        gaps = []
        if not row.from_email:
            gaps.append("FROM_EMAIL_MISSING")
        if not row.reply_to_email:
            gaps.append("REPLY_TO_MISSING")
        if row.status not in {SenderProviderConfigStatus.READY, SenderProviderConfigStatus.CONFIGURED}:
            gaps.append("PROVIDER_METADATA_NOT_READY")
        if row.provider_type == EmailProviderType.CPANEL_SMTP:
            for key, value in {"SMTP_HOST": self.settings.smtp_host, "SMTP_USERNAME": self.settings.smtp_username, "SMTP_PASSWORD": self.settings.smtp_password}.items():
                if not value:
                    gaps.append(f"{key}_MISSING")
        return not gaps, gaps, row
