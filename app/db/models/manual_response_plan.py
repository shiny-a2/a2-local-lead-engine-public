from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ManualResponsePlan(TimestampMixin, Base):
    __tablename__ = "manual_response_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    response_goal: Mapped[str] = mapped_column(String(255), nullable=False)
    recommended_tone: Mapped[str] = mapped_column(String(120), nullable=False)
    key_points_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    claims_allowed_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    claims_to_avoid_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    offer_package: Mapped[str] = mapped_column(String(120), nullable=False)
    modules_to_mention_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    pricing_strategy: Mapped[str] = mapped_column(String(120), nullable=False)
    cta_suggestion: Mapped[str] = mapped_column(String(255), nullable=False)
    manual_notes_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
