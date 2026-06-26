from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class RiskRegisterItem(Base):
    __tablename__ = "risk_register_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_audit_run_id: Mapped[int] = mapped_column(ForeignKey("pilot_audit_runs.id"))
    risk_code: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    affected_phases_json: Mapped[list] = mapped_column(JSON, nullable=False)
    root_cause: Mapped[str] = mapped_column(String(1000), nullable=False)
    mitigation: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(60), nullable=False)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
