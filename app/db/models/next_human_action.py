from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanTaskPriority, NextHumanActionStatus, NextHumanActionType
from app.db.base import Base, TimestampMixin


class NextHumanAction(TimestampMixin, Base):
    __tablename__ = "next_human_actions"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    action_type: Mapped[NextHumanActionType] = mapped_column(
        Enum(NextHumanActionType, native_enum=False)
    )
    priority: Mapped[HumanTaskPriority] = mapped_column(Enum(HumanTaskPriority, native_enum=False))
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[NextHumanActionStatus] = mapped_column(
        Enum(NextHumanActionStatus, native_enum=False)
    )
