from sqlalchemy.orm import Session

from app.core.enums import BounceProcessingMode, InboxMonitoringMode, MailboxReadinessStatus
from app.db.models.mailbox_readiness_check import MailboxReadinessCheck
from app.db.models.sender_identity_profile import SenderIdentityProfile
from app.settings import Settings


class MailboxReadinessService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def record(self, profile: SenderIdentityProfile | None = None) -> MailboxReadinessCheck:
        reply_to = self.settings.mailbox_reply_to_email or (profile.reply_to_email if profile else "")
        status = (
            MailboxReadinessStatus.READY_WITH_WARNINGS
            if reply_to
            else MailboxReadinessStatus.NOT_CONFIGURED
        )
        if self.settings.mailbox_monitoring_mode == "planned_only":
            status = MailboxReadinessStatus.FUTURE_PHASE_REQUIRED if not reply_to else status
        row = MailboxReadinessCheck(
            sender_profile_id=profile.id if profile else None,
            reply_to_email=reply_to,
            inbox_monitoring_mode=InboxMonitoringMode(self.settings.mailbox_monitoring_mode),
            bounce_processing_mode=BounceProcessingMode(self.settings.bounce_processing_mode),
            readiness_status=status,
            notes_json=[
                "No IMAP, inbox sync, bounce parsing, or provider webhook is implemented in Phase 9.",
                "Reply/bounce handling belongs to Phase 10/11.",
            ],
        )
        self.session.add(row)
        self.session.flush()
        return row
