from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PricingStrategy
from app.db.base import Base, utc_now


class PricingGuidanceRecord(Base):
    __tablename__ = "pricing_guidance_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    pricing_strategy: Mapped[PricingStrategy] = mapped_column(Enum(PricingStrategy, native_enum=False))
    internal_price_band: Mapped[str | None] = mapped_column(String(120), nullable=True)
    show_price_to_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_quote_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scope_questions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    pricing_notes_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    blocked_price_claims_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
