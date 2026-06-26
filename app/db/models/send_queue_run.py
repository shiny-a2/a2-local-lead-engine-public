from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SendQueueOperation, SendQueueRunStatus
from app.db.base import Base, utc_now


class SendQueueRun(Base):
    __tablename__ = "send_queue_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    operation: Mapped[SendQueueOperation] = mapped_column(Enum(SendQueueOperation, native_enum=False))
    status: Mapped[SendQueueRunStatus] = mapped_column(Enum(SendQueueRunStatus, native_enum=False))
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    input_approved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    queued_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    send_attempted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
