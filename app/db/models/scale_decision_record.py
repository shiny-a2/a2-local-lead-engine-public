from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class ScaleDecisionRecord(Base):
    __tablename__ = "scale_decision_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_audit_run_id: Mapped[int] = mapped_column(ForeignKey("pilot_audit_runs.id"))
    decision: Mapped[str] = mapped_column(String(80), nullable=False)
    ready_for_scale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sample_size_ok: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    limits_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
