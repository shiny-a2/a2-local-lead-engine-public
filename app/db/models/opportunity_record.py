from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import OpportunityStatus, OpportunityType
from app.db.base import Base, TimestampMixin


class OpportunityRecord(TimestampMixin, Base):
    __tablename__ = "opportunity_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    source_inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"), unique=True)
    opportunity_status: Mapped[OpportunityStatus] = mapped_column(Enum(OpportunityStatus, native_enum=False))
    opportunity_type: Mapped[OpportunityType] = mapped_column(Enum(OpportunityType, native_enum=False))
    priority: Mapped[str] = mapped_column(String(40), nullable=False)
    estimated_value_band: Mapped[str | None] = mapped_column(String(80), nullable=True)
    confidence: Mapped[float] = mapped_column(default=0.0, nullable=False)
