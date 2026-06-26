from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import LeadResponseTimelineEventType
from app.db.base import Base, utc_now


class LeadResponseTimeline(Base):
    __tablename__ = "lead_response_timeline"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    event_type: Mapped[LeadResponseTimelineEventType] = mapped_column(Enum(LeadResponseTimelineEventType, native_enum=False))
    event_source: Mapped[str] = mapped_column(String(120), nullable=False)
    event_summary: Mapped[str] = mapped_column(String(500), nullable=False)
    related_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    related_inbound_message_id: Mapped[int | None] = mapped_column(ForeignKey("inbound_email_messages.id"), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
