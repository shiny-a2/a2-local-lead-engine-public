from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class SendSuppressionCheck(Base):
    __tablename__ = "send_suppression_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_send_queue_id: Mapped[int] = mapped_column(ForeignKey("email_send_queue.id"))
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    suppression_hit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suppression_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    checked_at: Mapped[datetime] = mapped_column(default=utc_now)
