from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SourceName
from app.db.base import Base, utc_now


class SourceRequest(Base):
    __tablename__ = "source_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_run_id: Mapped[int] = mapped_column(ForeignKey("source_runs.id"), nullable=False)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    request_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_url_redacted: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    request_params_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cache_hit: Mapped[bool] = mapped_column(default=False, nullable=False)
    error_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    source_run = relationship("SourceRun", back_populates="requests")

