from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import GateSeverity, OfferReadinessGateName
from app.db.base import Base, utc_now


class OfferReadinessGate(Base):
    __tablename__ = "offer_readiness_gates"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    gate_name: Mapped[OfferReadinessGateName] = mapped_column(Enum(OfferReadinessGateName, native_enum=False))
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[GateSeverity] = mapped_column(Enum(GateSeverity, native_enum=False))
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
