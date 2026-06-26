from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanReviewDecisionValue
from app.db.base import Base, utc_now


class HumanReviewDecision(Base):
    __tablename__ = "human_review_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    human_review_run_id: Mapped[int] = mapped_column(ForeignKey("human_review_runs.id"))
    queue_item_id: Mapped[int] = mapped_column(ForeignKey("human_review_queue_items.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    decision: Mapped[HumanReviewDecisionValue] = mapped_column(Enum(HumanReviewDecisionValue, native_enum=False))
    reviewer: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
