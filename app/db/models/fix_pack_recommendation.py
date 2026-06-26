from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class FixPackRecommendation(Base):
    __tablename__ = "fix_pack_recommendations"
    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_audit_run_id: Mapped[int] = mapped_column(ForeignKey("pilot_audit_runs.id"))
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    root_cause: Mapped[str] = mapped_column(String(1000), nullable=False)
    affected_phases_json: Mapped[list] = mapped_column(JSON, nullable=False)
    risk_if_not_fixed: Mapped[str] = mapped_column(String(1000), nullable=False)
    acceptance_criteria: Mapped[str] = mapped_column(String(1000), nullable=False)
    codex_ready_summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="OPEN", nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
