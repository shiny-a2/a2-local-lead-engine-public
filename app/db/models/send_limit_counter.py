from datetime import datetime

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SendLimitCounterType
from app.db.base import Base, TimestampMixin


class SendLimitCounter(TimestampMixin, Base):
    __tablename__ = "send_limit_counters"
    id: Mapped[int] = mapped_column(primary_key=True)
    counter_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    counter_type: Mapped[SendLimitCounterType] = mapped_column(Enum(SendLimitCounterType, native_enum=False))
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    window_started_at: Mapped[datetime] = mapped_column(nullable=False)
    window_ends_at: Mapped[datetime] = mapped_column(nullable=False)
