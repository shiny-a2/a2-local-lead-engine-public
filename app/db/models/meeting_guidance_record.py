from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class MeetingGuidanceRecord(Base):
    __tablename__ = "meeting_guidance_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    meeting_requested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    automatic_scheduling_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(500), nullable=False)
    suggested_questions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    manual_owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
