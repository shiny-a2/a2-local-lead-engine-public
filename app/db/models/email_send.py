from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailSendStatus
from app.db.base import Base, utc_now


class EmailSend(Base):
    __tablename__ = "email_sends"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int | None] = mapped_column(ForeignKey("email_drafts.id"), nullable=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"), nullable=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[EmailSendStatus] = mapped_column(
        Enum(EmailSendStatus, native_enum=False),
        default=EmailSendStatus.PENDING_APPROVAL,
        nullable=False,
    )
    provider: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    blocked_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

