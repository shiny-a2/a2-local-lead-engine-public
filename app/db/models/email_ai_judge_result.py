from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailAiJudgeDecision
from app.db.base import Base, utc_now


class EmailAiJudgeResult(Base):
    __tablename__ = "email_ai_judge_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_judge_run_id: Mapped[int] = mapped_column(ForeignKey("email_judge_runs.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    judge_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    judge_prompt_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    overall_quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    truthfulness_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_alignment_score: Mapped[float] = mapped_column(Float, nullable=False)
    personalization_score: Mapped[float] = mapped_column(Float, nullable=False)
    human_likeness_score: Mapped[float] = mapped_column(Float, nullable=False)
    non_promotional_score: Mapped[float] = mapped_column(Float, nullable=False)
    economic_claim_safety_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    spam_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    cta_quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    decision: Mapped[EmailAiJudgeDecision] = mapped_column(Enum(EmailAiJudgeDecision, native_enum=False))
    findings_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    rewrite_brief_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
