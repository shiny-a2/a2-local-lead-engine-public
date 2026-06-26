from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import LeadScoreDecision
from app.db.base import Base, utc_now


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    website_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    business_fit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    contact_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision: Mapped[LeadScoreDecision] = mapped_column(Enum(LeadScoreDecision, native_enum=False))
    decision_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    lead = relationship("Lead", back_populates="scores")

