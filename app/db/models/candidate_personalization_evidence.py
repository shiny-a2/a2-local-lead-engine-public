from datetime import datetime

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class CandidatePersonalizationEvidence(Base):
    __tablename__ = "candidate_personalization_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    evidence_type: Mapped[str] = mapped_column(String(120), nullable=False)
    evidence_value: Mapped[str] = mapped_column(String(1000), nullable=False)
    evidence_source: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    allowed_for_future_copy: Mapped[bool] = mapped_column(default=False, nullable=False)
    requires_verification: Mapped[bool] = mapped_column(default=True, nullable=False)
    risk_flag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supporting_raw_record_ids_json: Mapped[list[int]] = mapped_column(
        JSON, default=list, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    candidate_business = relationship("CandidateBusiness", back_populates="evidence")

