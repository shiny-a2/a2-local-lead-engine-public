from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanSalesGateName
from app.db.base import Base, utc_now


class HumanSalesControlGate(Base):
    __tablename__ = "human_sales_control_gates"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    gate_name: Mapped[HumanSalesGateName] = mapped_column(Enum(HumanSalesGateName, native_enum=False))
    passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
