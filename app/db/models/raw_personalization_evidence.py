from datetime import datetime

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class RawPersonalizationEvidence(Base):
    __tablename__ = "raw_personalization_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_source_record_id: Mapped[int] = mapped_column(ForeignKey("raw_source_records.id"))
    source_run_id: Mapped[int] = mapped_column(ForeignKey("source_runs.id"))
    evidence_type: Mapped[str] = mapped_column(String(120), nullable=False)
    evidence_value: Mapped[str] = mapped_column(String(1000), nullable=False)
    evidence_source: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    allowed_for_future_copy: Mapped[bool] = mapped_column(default=False, nullable=False)
    requires_verification: Mapped[bool] = mapped_column(default=True, nullable=False)
    risk_flag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    raw_source_record = relationship("RawSourceRecord", back_populates="evidence")
