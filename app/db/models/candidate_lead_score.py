from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ReplyProbabilityBand
from app.db.base import Base, utc_now


class CandidateLeadScore(Base):
    __tablename__ = "candidate_lead_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    scoring_run_id: Mapped[int] = mapped_column(ForeignKey("scoring_runs.id"))
    overall_lead_score: Mapped[float] = mapped_column(Float, nullable=False)
    website_opportunity_score: Mapped[float] = mapped_column(Float, nullable=False)
    business_fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    contact_readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    personalization_potential_score: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_safety_score: Mapped[float] = mapped_column(Float, nullable=False)
    reply_probability_band: Mapped[ReplyProbabilityBand] = mapped_column(
        Enum(ReplyProbabilityBand, native_enum=False)
    )
    risk_penalty: Mapped[float] = mapped_column(Float, nullable=False)
    score_version: Mapped[str] = mapped_column(String(40), nullable=False)
    scoring_profile: Mapped[str] = mapped_column(String(120), nullable=False)
    positive_reasons_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    negative_reasons_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    score_reasons_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    risk_flags_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
