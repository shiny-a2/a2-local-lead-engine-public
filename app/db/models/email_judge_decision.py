from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailJudgeDecisionValue
from app.db.base import Base, utc_now


class EmailJudgeDecision(Base):
    __tablename__ = "email_judge_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_judge_run_id: Mapped[int] = mapped_column(ForeignKey("email_judge_runs.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    decision: Mapped[EmailJudgeDecisionValue] = mapped_column(Enum(EmailJudgeDecisionValue, native_enum=False))
    quality_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    ready_for_phase9: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_variant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rewrite_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    warnings_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
