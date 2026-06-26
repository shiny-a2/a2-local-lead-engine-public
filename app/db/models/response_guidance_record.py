from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ResponseGuidanceType
from app.db.base import Base, utc_now


class ResponseGuidanceRecord(Base):
    __tablename__ = "response_guidance_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    response_type: Mapped[ResponseGuidanceType] = mapped_column(Enum(ResponseGuidanceType, native_enum=False))
    response_goal: Mapped[str] = mapped_column(String(255), nullable=False)
    key_points_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    things_to_avoid_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommended_tone: Mapped[str] = mapped_column(String(120), nullable=False)
    cta_recommendation: Mapped[str] = mapped_column(String(255), nullable=False)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
