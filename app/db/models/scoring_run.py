from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ScoringRunOperation, ScoringRunStatus
from app.db.base import Base, utc_now


class ScoringRun(Base):
    __tablename__ = "scoring_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    operation: Mapped[ScoringRunOperation] = mapped_column(
        Enum(ScoringRunOperation, native_enum=False)
    )
    status: Mapped[ScoringRunStatus] = mapped_column(Enum(ScoringRunStatus, native_enum=False))
    dry_run: Mapped[bool] = mapped_column(default=True, nullable=False)
    scoring_profile: Mapped[str] = mapped_column(String(120), nullable=False)
    score_version: Mapped[str] = mapped_column(String(40), nullable=False)
    input_candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scored_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ready_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manual_review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
