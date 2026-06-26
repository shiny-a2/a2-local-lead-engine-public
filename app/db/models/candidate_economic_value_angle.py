from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ClaimStrength, EconomicAngleType
from app.db.base import Base, utc_now


class CandidateEconomicValueAngle(Base):
    __tablename__ = "candidate_economic_value_angles"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    angle_type: Mapped[EconomicAngleType] = mapped_column(Enum(EconomicAngleType, native_enum=False))
    angle_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    claim_strength: Mapped[ClaimStrength] = mapped_column(Enum(ClaimStrength, native_enum=False))
    allowed_for_future_copy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_verification: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    blocked_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
