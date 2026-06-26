from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class PhaseReadinessAudit(Base):
    __tablename__ = "phase_readiness_audits"
    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_audit_run_id: Mapped[int] = mapped_column(ForeignKey("pilot_audit_runs.id"))
    phase_number: Mapped[int] = mapped_column(nullable=False)
    phase_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    implemented: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocker: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
