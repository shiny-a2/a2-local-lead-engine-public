from datetime import datetime

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class CandidateBusinessInsight(Base):
    __tablename__ = "candidate_business_insights"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    campaign_lane: Mapped[str] = mapped_column(String(80), nullable=False)
    business_context_summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    likely_customer_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    main_friction_points_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    opportunity_summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
