from datetime import datetime

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ProviderCircuitStatus
from app.db.base import Base, TimestampMixin


class ProviderCircuitBreaker(TimestampMixin, Base):
    __tablename__ = "provider_circuit_breakers"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_slug: Mapped[str] = mapped_column(String(120), nullable=False)
    consecutive_failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    circuit_status: Mapped[ProviderCircuitStatus] = mapped_column(Enum(ProviderCircuitStatus, native_enum=False))
    disabled_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(nullable=True)
    opened_at: Mapped[datetime | None] = mapped_column(nullable=True)
