from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import NormalizationOperation, NormalizationRunStatus
from app.db.base import Base, utc_now


class NormalizationRun(Base):
    __tablename__ = "normalization_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    source_run_id: Mapped[int | None] = mapped_column(ForeignKey("source_runs.id"), nullable=True)
    operation: Mapped[NormalizationOperation] = mapped_column(
        Enum(NormalizationOperation, native_enum=False)
    )
    status: Mapped[NormalizationRunStatus] = mapped_column(
        Enum(NormalizationRunStatus, native_enum=False),
        default=NormalizationRunStatus.STARTED,
        nullable=False,
    )
    dry_run: Mapped[bool] = mapped_column(default=True, nullable=False)
    input_raw_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    candidate_created_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    candidate_updated_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_cluster_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manual_review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

