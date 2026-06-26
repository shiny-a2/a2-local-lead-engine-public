from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import LeadResponseLatestStatus
from app.db.base import Base, TimestampMixin, utc_now


class LeadResponseStatus(TimestampMixin, Base):
    __tablename__ = "lead_response_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    latest_status: Mapped[LeadResponseLatestStatus] = mapped_column(Enum(LeadResponseLatestStatus, native_enum=False))
    latest_inbound_message_id: Mapped[int | None] = mapped_column(ForeignKey("inbound_email_messages.id"), nullable=True)
    latest_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    human_action_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now, nullable=False)
