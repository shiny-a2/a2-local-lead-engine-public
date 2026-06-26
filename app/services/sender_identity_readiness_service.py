from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SenderIdentityStatus, SenderProviderType
from app.db.models.sender_identity_profile import SenderIdentityProfile
from app.settings import Settings


class SenderIdentityReadinessService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def ensure_default(self) -> SenderIdentityProfile:
        profile = self.session.scalar(
            select(SenderIdentityProfile).where(
                SenderIdentityProfile.profile_slug == self.settings.default_sender_profile_slug
            )
        )
        if profile:
            return profile
        from_email = self.settings.default_from_email or self.settings.smtp_from_email
        reply_to = self.settings.default_reply_to_email or self.settings.smtp_reply_to or from_email
        domain = from_email.split("@")[-1] if "@" in from_email else ""
        status = SenderIdentityStatus.CONFIGURED if from_email and reply_to else SenderIdentityStatus.NEEDS_REVIEW
        profile = SenderIdentityProfile(
            profile_slug=self.settings.default_sender_profile_slug,
            provider_type=SenderProviderType.MANUAL_PLACEHOLDER,
            from_email=from_email,
            from_name=self.settings.default_from_name,
            reply_to_email=reply_to,
            domain=domain,
            status=status,
            readiness_notes_json=[
                "Phase 9 stores sender metadata only.",
                "SMTP credentials are not stored in DB.",
            ],
        )
        self.session.add(profile)
        self.session.flush()
        return profile

    def readiness(self) -> tuple[bool, list[str], SenderIdentityProfile]:
        profile = self.ensure_default()
        ok = bool(profile.from_email and profile.reply_to_email) and profile.status in {
            SenderIdentityStatus.CONFIGURED,
            SenderIdentityStatus.MANUAL_VERIFIED,
        }
        notes = list(profile.readiness_notes_json or [])
        if not ok:
            notes.append("sender_identity_not_configured")
        return ok, notes, profile
