from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SourceName, SourceOperation, SourceRunStatus
from app.db.base import Base, utc_now


class SourceRun(Base):
    __tablename__ = "source_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    operation: Mapped[SourceOperation] = mapped_column(Enum(SourceOperation, native_enum=False))
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[SourceRunStatus] = mapped_column(
        Enum(SourceRunStatus, native_enum=False), default=SourceRunStatus.STARTED
    )
    dry_run: Mapped[bool] = mapped_column(default=True, nullable=False)
    requested_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stored_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    requests = relationship("SourceRequest", back_populates="source_run")
    raw_records = relationship("RawSourceRecord", back_populates="source_run")

