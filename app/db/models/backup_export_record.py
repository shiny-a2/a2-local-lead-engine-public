from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class BackupExportRecord(Base):
    __tablename__ = "backup_export_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    pilot_audit_run_id: Mapped[int | None] = mapped_column(ForeignKey("pilot_audit_runs.id"), nullable=True)
    export_type: Mapped[str] = mapped_column(String(80), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(60), nullable=False)
    secrets_included: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
