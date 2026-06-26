from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import BounceProcessingMode, InboxMonitoringMode, MailboxReadinessStatus
from app.db.base import Base, utc_now


class MailboxReadinessCheck(Base):
    __tablename__ = "mailbox_readiness_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_profile_id: Mapped[int | None] = mapped_column(ForeignKey("sender_identity_profiles.id"), nullable=True)
    reply_to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    inbox_monitoring_mode: Mapped[InboxMonitoringMode] = mapped_column(Enum(InboxMonitoringMode, native_enum=False))
    bounce_processing_mode: Mapped[BounceProcessingMode] = mapped_column(Enum(BounceProcessingMode, native_enum=False))
    readiness_status: Mapped[MailboxReadinessStatus] = mapped_column(Enum(MailboxReadinessStatus, native_enum=False))
    notes_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
