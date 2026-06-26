from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanReviewOperation, HumanReviewRunStatus
from app.db.base import Base, utc_now


class HumanReviewRun(Base):
    __tablename__ = "human_review_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    operation: Mapped[HumanReviewOperation] = mapped_column(Enum(HumanReviewOperation, native_enum=False))
    status: Mapped[HumanReviewRunStatus] = mapped_column(Enum(HumanReviewRunStatus, native_enum=False))
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    input_draft_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    queued_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_with_warnings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    edit_required_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    returned_to_rewrite_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    returned_to_judge_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    held_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
