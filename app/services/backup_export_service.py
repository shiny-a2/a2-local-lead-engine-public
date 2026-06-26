from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.backup_export_record import BackupExportRecord


class BackupExportService:
    def __init__(self, session: Session):
        self.session = session

    def record_manifest(self, audit_run_id: int | None, out_dir: Path = Path("exports")) -> BackupExportRecord:
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = out_dir / "phase14-export-manifest.txt"
        manifest.write_text("Phase 14 export manifest. .env files and secrets are excluded.\n", encoding="utf-8")
        row = BackupExportRecord(
            pilot_audit_run_id=audit_run_id,
            export_type="manifest_only",
            file_path=str(manifest),
            status="CREATED",
            secrets_included=False,
            metadata_json={"env_files_exported": False},
        )
        self.session.add(row)
        self.session.flush()
        return row
