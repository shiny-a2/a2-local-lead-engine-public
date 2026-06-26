from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import DeliveryEventType, EmailProviderType
from app.db.base import Base, utc_now


class DeliveryEvent(Base):
    __tablename__ = "delivery_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_send_attempt_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_attempts.id"), nullable=True)
    email_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    provider_type: Mapped[EmailProviderType] = mapped_column(Enum(EmailProviderType, native_enum=False))
    event_type: Mapped[DeliveryEventType] = mapped_column(Enum(DeliveryEventType, native_enum=False))
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
