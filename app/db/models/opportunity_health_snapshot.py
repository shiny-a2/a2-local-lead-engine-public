from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import OpportunityHealthStatus
from app.db.base import Base, utc_now


class OpportunityHealthSnapshot(Base):
    __tablename__ = "opportunity_health_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    health_status: Mapped[OpportunityHealthStatus] = mapped_column(
        Enum(OpportunityHealthStatus, native_enum=False)
    )
    reply_quality_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scope_completeness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    customer_intent_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contact_reliability_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    proposal_readiness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    task_overdue_risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
