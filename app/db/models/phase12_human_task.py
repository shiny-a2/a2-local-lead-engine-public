from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanTaskPriority, HumanTaskStatus, Phase12TaskType
from app.db.base import Base, TimestampMixin


class Phase12HumanTask(TimestampMixin, Base):
    __tablename__ = "phase12_human_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int | None] = mapped_column(ForeignKey("opportunity_records.id"), nullable=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    inbound_message_id: Mapped[int | None] = mapped_column(ForeignKey("inbound_email_messages.id"), nullable=True)
    task_type: Mapped[Phase12TaskType] = mapped_column(Enum(Phase12TaskType, native_enum=False))
    priority: Mapped[HumanTaskPriority] = mapped_column(Enum(HumanTaskPriority, native_enum=False))
    status: Mapped[HumanTaskStatus] = mapped_column(Enum(HumanTaskStatus, native_enum=False))
    assigned_to: Mapped[str | None] = mapped_column(String(120), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(nullable=True)
    recommended_action: Mapped[str] = mapped_column(String(500), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
