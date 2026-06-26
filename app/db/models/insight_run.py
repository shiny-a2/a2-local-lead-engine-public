from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import InsightRunOperation, InsightRunStatus
from app.db.base import Base, utc_now


class InsightRun(Base):
    __tablename__ = "insight_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    operation: Mapped[InsightRunOperation] = mapped_column(Enum(InsightRunOperation, native_enum=False))
    status: Mapped[InsightRunStatus] = mapped_column(Enum(InsightRunStatus, native_enum=False))
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    input_candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    insight_created_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    offer_matched_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manual_review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
