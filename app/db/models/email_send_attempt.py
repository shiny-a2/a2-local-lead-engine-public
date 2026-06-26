from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailProviderType, ProviderStatus, SendAttemptStatus
from app.db.base import Base, utc_now


class EmailSendAttempt(Base):
    __tablename__ = "email_send_attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_send_queue_id: Mapped[int] = mapped_column(ForeignKey("email_send_queue.id"))
    provider_type: Mapped[EmailProviderType] = mapped_column(Enum(EmailProviderType, native_enum=False))
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    smtp_response_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_status: Mapped[ProviderStatus] = mapped_column(Enum(ProviderStatus, native_enum=False))
    attempt_status: Mapped[SendAttemptStatus] = mapped_column(Enum(SendAttemptStatus, native_enum=False))
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    error_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transient_error: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    permanent_error: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
