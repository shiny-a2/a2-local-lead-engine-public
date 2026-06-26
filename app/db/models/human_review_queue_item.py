from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanReviewQueueStatus
from app.db.base import Base, TimestampMixin


class HumanReviewQueueItem(TimestampMixin, Base):
    __tablename__ = "human_review_queue_items"
    __table_args__ = (UniqueConstraint("email_draft_variant_id", name="uq_review_queue_draft"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    human_review_run_id: Mapped[int] = mapped_column(ForeignKey("human_review_runs.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    phase8_decision_id: Mapped[int | None] = mapped_column(ForeignKey("email_judge_decisions.id"), nullable=True)
    queue_status: Mapped[HumanReviewQueueStatus] = mapped_column(Enum(HumanReviewQueueStatus, native_enum=False))
    priority_tier: Mapped[str | None] = mapped_column(String(80), nullable=True)
    campaign_lane: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reviewer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(nullable=True)
    review_lock_owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    lock_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
