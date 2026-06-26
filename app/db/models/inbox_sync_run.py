from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import InboxSyncOperation, InboxSyncStatus
from app.db.base import Base, utc_now


class InboxSyncRun(Base):
    __tablename__ = "inbox_sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    provider_type: Mapped[str] = mapped_column(String(80), nullable=False)
    mailbox: Mapped[str] = mapped_column(String(255), nullable=False)
    operation: Mapped[InboxSyncOperation] = mapped_column(Enum(InboxSyncOperation, native_enum=False))
    status: Mapped[InboxSyncStatus] = mapped_column(Enum(InboxSyncStatus, native_enum=False))
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    messages_seen: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    replies_detected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bounces_detected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    auto_replies_detected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
