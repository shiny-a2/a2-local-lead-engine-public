from datetime import datetime

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class VerifiedPersonalizationEvidence(Base):
    __tablename__ = "verified_personalization_evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    evidence_type: Mapped[str] = mapped_column(String(120), nullable=False)
    evidence_value: Mapped[str] = mapped_column(String(1000), nullable=False)
    evidence_source: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    allowed_for_future_copy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_verification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    risk_flag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supporting_urls_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    supporting_candidate_evidence_ids_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

