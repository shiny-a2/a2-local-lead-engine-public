from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Phase9Decision
from app.db.base import Base, utc_now


class Phase9CandidateDecision(Base):
    __tablename__ = "phase9_candidate_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    human_review_run_id: Mapped[int] = mapped_column(ForeignKey("human_review_runs.id"))
    queue_item_id: Mapped[int] = mapped_column(ForeignKey("human_review_queue_items.id"))
    decision: Mapped[Phase9Decision] = mapped_column(Enum(Phase9Decision, native_enum=False))
    ready_for_phase10: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_edit_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hold_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    warnings_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
