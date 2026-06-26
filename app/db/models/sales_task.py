from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanTaskPriority, SalesTaskStatus, SalesTaskType
from app.db.base import Base, TimestampMixin


class SalesTask(TimestampMixin, Base):
    __tablename__ = "sales_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    task_type: Mapped[SalesTaskType] = mapped_column(Enum(SalesTaskType, native_enum=False))
    priority: Mapped[HumanTaskPriority] = mapped_column(Enum(HumanTaskPriority, native_enum=False))
    status: Mapped[SalesTaskStatus] = mapped_column(Enum(SalesTaskStatus, native_enum=False))
    assigned_to: Mapped[str | None] = mapped_column(String(120), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
