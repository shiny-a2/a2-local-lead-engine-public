from datetime import datetime

from sqlalchemy import Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SourceName
from app.db.base import Base, utc_now


class SourceRateLimit(Base):
    __tablename__ = "source_rate_limits"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    window_key: Mapped[str] = mapped_column(String(120), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credit_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    window_started_at: Mapped[datetime] = mapped_column(nullable=False)
    window_ends_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

