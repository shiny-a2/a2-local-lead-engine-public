from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PainPointType
from app.db.base import Base, utc_now


class CandidatePainPointHypothesis(Base):
    __tablename__ = "candidate_pain_point_hypotheses"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    pain_point_type: Mapped[PainPointType] = mapped_column(Enum(PainPointType, native_enum=False))
    pain_point_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    requires_verification: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allowed_for_future_copy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
