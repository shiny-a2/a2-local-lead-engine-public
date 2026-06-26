from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UnsubscribeTokenStatus
from app.db.base import Base, utc_now


class UnsubscribeToken(Base):
    __tablename__ = "unsubscribe_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    email_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    status: Mapped[UnsubscribeTokenStatus] = mapped_column(Enum(UnsubscribeTokenStatus, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
