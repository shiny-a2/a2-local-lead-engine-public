from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ReplyClassificationValue, ReplyClassifierType
from app.db.base import Base, utc_now


class ReplyClassification(Base):
    __tablename__ = "reply_classifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    candidate_business_id: Mapped[int | None] = mapped_column(ForeignKey("candidate_businesses.id"), nullable=True)
    classification: Mapped[ReplyClassificationValue] = mapped_column(Enum(ReplyClassificationValue, native_enum=False))
    confidence: Mapped[float] = mapped_column(default=0.0, nullable=False)
    classifier_type: Mapped[ReplyClassifierType] = mapped_column(Enum(ReplyClassifierType, native_enum=False))
    signals_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    manual_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
