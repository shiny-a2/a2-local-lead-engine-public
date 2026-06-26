from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UnsubscribeEventSource
from app.db.base import Base, utc_now


class UnsubscribeEvent(Base):
    __tablename__ = "unsubscribe_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    unsubscribe_token_id: Mapped[int | None] = mapped_column(ForeignKey("unsubscribe_tokens.id"), nullable=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    event_source: Mapped[UnsubscribeEventSource] = mapped_column(Enum(UnsubscribeEventSource, native_enum=False))
    ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
