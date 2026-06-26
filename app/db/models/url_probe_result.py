from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UrlProbeStatus
from app.db.base import Base, utc_now


class UrlProbeResult(Base):
    __tablename__ = "url_probe_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    final_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_redirect: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    redirect_chain_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    content_sample_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    probe_status: Mapped[UrlProbeStatus] = mapped_column(Enum(UrlProbeStatus, native_enum=False))
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

