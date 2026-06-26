from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import InboundPartType
from app.db.base import Base, utc_now


class InboundMessagePart(Base):
    __tablename__ = "inbound_message_parts"

    id: Mapped[int] = mapped_column(primary_key=True)
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    part_type: Mapped[InboundPartType] = mapped_column(Enum(InboundPartType, native_enum=False))
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
