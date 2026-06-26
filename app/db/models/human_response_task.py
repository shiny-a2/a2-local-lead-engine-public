from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanResponseTaskType, HumanTaskPriority, HumanTaskStatus
from app.db.base import Base, TimestampMixin


class HumanResponseTask(TimestampMixin, Base):
    __tablename__ = "human_response_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    inbound_message_id: Mapped[int | None] = mapped_column(ForeignKey("inbound_email_messages.id"), nullable=True)
    task_type: Mapped[HumanResponseTaskType] = mapped_column(Enum(HumanResponseTaskType, native_enum=False))
    priority: Mapped[HumanTaskPriority] = mapped_column(Enum(HumanTaskPriority, native_enum=False))
    status: Mapped[HumanTaskStatus] = mapped_column(Enum(HumanTaskStatus, native_enum=False))
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
