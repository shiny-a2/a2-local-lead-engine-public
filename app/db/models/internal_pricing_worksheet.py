from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PricingWorksheetStatus
from app.db.base import Base, TimestampMixin


class InternalPricingWorksheet(TimestampMixin, Base):
    __tablename__ = "internal_pricing_worksheets"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"), unique=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    pricing_status: Mapped[PricingWorksheetStatus] = mapped_column(
        Enum(PricingWorksheetStatus, native_enum=False)
    )
    base_package: Mapped[str | None] = mapped_column(String(120), nullable=True)
    selected_modules_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    manual_base_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    manual_module_adjustments_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    manual_discount: Mapped[float | None] = mapped_column(Float, nullable=True)
    manual_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    final_manual_quote: Mapped[float | None] = mapped_column(Float, nullable=True)
    quote_approved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quote_approved_at: Mapped[datetime | None] = mapped_column(nullable=True)
