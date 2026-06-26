from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Phase13DecisionValue
from app.db.base import Base, utc_now


class Phase13Decision(Base):
    __tablename__ = "phase13_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    decision: Mapped[Phase13DecisionValue] = mapped_column(
        Enum(Phase13DecisionValue, native_enum=False)
    )
    ready_for_phase14: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_action_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    warnings_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
