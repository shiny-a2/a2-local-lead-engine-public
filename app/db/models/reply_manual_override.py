from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import LeadResponseLatestStatus, ReplyClassificationValue
from app.db.base import Base, utc_now


class ReplyManualOverride(Base):
    __tablename__ = "reply_manual_overrides"

    id: Mapped[int] = mapped_column(primary_key=True)
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    candidate_business_id: Mapped[int | None] = mapped_column(ForeignKey("candidate_businesses.id"), nullable=True)
    old_classification: Mapped[ReplyClassificationValue] = mapped_column(Enum(ReplyClassificationValue, native_enum=False))
    new_classification: Mapped[ReplyClassificationValue] = mapped_column(Enum(ReplyClassificationValue, native_enum=False))
    old_status: Mapped[LeadResponseLatestStatus | None] = mapped_column(Enum(LeadResponseLatestStatus, native_enum=False), nullable=True)
    new_status: Mapped[LeadResponseLatestStatus | None] = mapped_column(Enum(LeadResponseLatestStatus, native_enum=False), nullable=True)
    reviewer: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
