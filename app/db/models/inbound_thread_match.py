from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import InboundMatchMethod
from app.db.base import Base, utc_now


class InboundThreadMatch(Base):
    __tablename__ = "inbound_thread_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    email_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    candidate_business_id: Mapped[int | None] = mapped_column(ForeignKey("candidate_businesses.id"), nullable=True)
    match_method: Mapped[InboundMatchMethod] = mapped_column(Enum(InboundMatchMethod, native_enum=False))
    match_confidence: Mapped[float] = mapped_column(default=0.0, nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
