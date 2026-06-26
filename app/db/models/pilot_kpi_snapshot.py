from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class PilotKpiSnapshot(Base):
    __tablename__ = "pilot_kpi_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_audit_run_id: Mapped[int] = mapped_column(ForeignKey("pilot_audit_runs.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    metric_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metric_context_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
