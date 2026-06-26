from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import CampaignFitStatus, CampaignLane
from app.db.base import Base, utc_now


class CampaignFitAssessment(Base):
    __tablename__ = "campaign_fit_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    scoring_run_id: Mapped[int] = mapped_column(ForeignKey("scoring_runs.id"))
    campaign_lane: Mapped[CampaignLane] = mapped_column(Enum(CampaignLane, native_enum=False))
    campaign_fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    campaign_fit_status: Mapped[CampaignFitStatus] = mapped_column(
        Enum(CampaignFitStatus, native_enum=False)
    )
    decision_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
