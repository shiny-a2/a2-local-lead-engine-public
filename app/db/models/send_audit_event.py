from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SendAuditAction
from app.db.base import Base, utc_now


class SendAuditEvent(Base):
    __tablename__ = "send_audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[SendAuditAction] = mapped_column(Enum(SendAuditAction, native_enum=False))
    before_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
