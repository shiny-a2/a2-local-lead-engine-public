from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import FollowupType, ManualFollowupStatus
from app.db.base import Base, TimestampMixin


class ManualFollowupPlan(TimestampMixin, Base):
    __tablename__ = "manual_followup_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"), unique=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    followup_type: Mapped[FollowupType] = mapped_column(Enum(FollowupType, native_enum=False))
    not_before: Mapped[datetime | None] = mapped_column(nullable=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ManualFollowupStatus] = mapped_column(
        Enum(ManualFollowupStatus, native_enum=False)
    )
