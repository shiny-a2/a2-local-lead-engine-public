from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import FollowupType
from app.db.base import Base, utc_now


class FollowupEligibilityRecord(Base):
    __tablename__ = "followup_eligibility_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    followup_type: Mapped[FollowupType] = mapped_column(Enum(FollowupType, native_enum=False))
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    not_before: Mapped[datetime | None] = mapped_column(nullable=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
