from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import OpportunityCloseReason
from app.db.base import Base, utc_now


class OpportunityCloseRecord(Base):
    __tablename__ = "opportunity_close_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    close_reason: Mapped[OpportunityCloseReason] = mapped_column(
        Enum(OpportunityCloseReason, native_enum=False)
    )
    closed_by: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
