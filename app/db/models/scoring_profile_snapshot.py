from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class ScoringProfileSnapshot(Base):
    __tablename__ = "scoring_profile_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    scoring_run_id: Mapped[int] = mapped_column(ForeignKey("scoring_runs.id"))
    scoring_profile: Mapped[str] = mapped_column(String(120), nullable=False)
    score_version: Mapped[str] = mapped_column(String(40), nullable=False)
    formula_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    gate_policy_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    campaign_lane_policy_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

