from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class RetentionPolicyRecord(Base):
    __tablename__ = "retention_policy_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_audit_run_id: Mapped[int | None] = mapped_column(ForeignKey("pilot_audit_runs.id"), nullable=True)
    policy_name: Mapped[str] = mapped_column(String(120), nullable=False)
    retention_days: Mapped[int] = mapped_column(nullable=False)
    policy_status: Mapped[str] = mapped_column(String(60), nullable=False)
    notes_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
