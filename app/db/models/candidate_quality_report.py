from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CandidateQualityDecision
from app.db.base import Base, utc_now


class CandidateQualityReport(Base):
    __tablename__ = "candidate_quality_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    identity_score: Mapped[float] = mapped_column(Float, nullable=False)
    location_score: Mapped[float] = mapped_column(Float, nullable=False)
    category_score: Mapped[float] = mapped_column(Float, nullable=False)
    contact_hint_score: Mapped[float] = mapped_column(Float, nullable=False)
    source_diversity_score: Mapped[float] = mapped_column(Float, nullable=False)
    personalization_evidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    readiness_decision: Mapped[CandidateQualityDecision] = mapped_column(
        Enum(CandidateQualityDecision, native_enum=False)
    )
    quality_notes_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    candidate_business = relationship("CandidateBusiness", back_populates="quality_reports")

