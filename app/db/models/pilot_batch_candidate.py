from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import CampaignLane, PriorityTier
from app.db.base import Base, utc_now


class PilotBatchCandidate(Base):
    __tablename__ = "pilot_batch_candidates"
    __table_args__ = (UniqueConstraint("batch_name", "candidate_business_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    scoring_run_id: Mapped[int] = mapped_column(ForeignKey("scoring_runs.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    batch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    batch_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    priority_tier: Mapped[PriorityTier] = mapped_column(Enum(PriorityTier, native_enum=False))
    campaign_lane: Mapped[CampaignLane] = mapped_column(Enum(CampaignLane, native_enum=False))
    selection_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

