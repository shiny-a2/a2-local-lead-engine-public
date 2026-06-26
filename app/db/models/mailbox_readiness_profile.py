from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Phase11MailboxStatus
from app.db.base import Base, TimestampMixin


class MailboxReadinessProfile(TimestampMixin, Base):
    __tablename__ = "mailbox_readiness_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    provider_type: Mapped[str] = mapped_column(String(80), nullable=False)
    mailbox_email: Mapped[str] = mapped_column(String(255), nullable=False)
    imap_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    imap_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[Phase11MailboxStatus] = mapped_column(Enum(Phase11MailboxStatus, native_enum=False))
    last_sync_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_seen_uid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
