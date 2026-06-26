from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanApprovalType
from app.db.base import Base, utc_now


class HumanApprovalLedger(Base):
    __tablename__ = "human_approval_ledger"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    approval_type: Mapped[HumanApprovalType] = mapped_column(
        Enum(HumanApprovalType, native_enum=False)
    )
    approved_by: Mapped[str] = mapped_column(String(120), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
