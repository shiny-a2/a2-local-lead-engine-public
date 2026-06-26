from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import BounceSource, BounceType
from app.db.base import Base, utc_now


class BounceEvent(Base):
    __tablename__ = "bounce_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    inbound_message_id: Mapped[int | None] = mapped_column(ForeignKey("inbound_email_messages.id"), nullable=True)
    delivery_event_id: Mapped[int | None] = mapped_column(ForeignKey("delivery_events.id"), nullable=True)
    email_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    candidate_business_id: Mapped[int | None] = mapped_column(ForeignKey("candidate_businesses.id"), nullable=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    bounce_source: Mapped[BounceSource] = mapped_column(Enum(BounceSource, native_enum=False))
    bounce_type: Mapped[BounceType] = mapped_column(Enum(BounceType, native_enum=False))
    bounce_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    diagnostic_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    suppression_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
