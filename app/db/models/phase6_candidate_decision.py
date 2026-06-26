from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Phase6Decision
from app.db.base import Base, utc_now


class Phase6CandidateDecision(Base):
    __tablename__ = "phase6_candidate_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    decision: Mapped[Phase6Decision] = mapped_column(Enum(Phase6Decision, native_enum=False))
    ready_for_phase7: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hold_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    warnings_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
