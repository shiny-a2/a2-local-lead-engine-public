import csv
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.enums import SuppressionImportStatus, SuppressionReason
from app.core.run_context import RunContext
from app.db.models.suppression import SuppressionList
from app.db.models.suppression_import_run import SuppressionImportRun


class SuppressionImportService:
    def __init__(self, session: Session):
        self.session = session

    def run(self, path: Path, commit: bool) -> SuppressionImportRun:
        errors: list[str] = []
        valid: list[dict[str, str]] = []
        with path.open(newline="", encoding="utf-8") as handle:
            for index, row in enumerate(csv.DictReader(handle), start=2):
                kind = (row.get("type") or "").strip()
                value = (row.get("value") or "").strip().lower()
                reason = (row.get("reason") or "").strip()
                if kind not in {"email", "domain"} or not value or not reason:
                    errors.append(f"row {index}: invalid")
                    continue
                valid.append({"type": kind, "value": value, "reason": reason})
        run = SuppressionImportRun(run_id=RunContext().run_id, file_name=str(path), dry_run=not commit, total_rows=len(valid) + len(errors), valid_rows=len(valid), invalid_rows=len(errors), imported_rows=0, status=SuppressionImportStatus.DRY_RUN_ONLY.value if not commit else SuppressionImportStatus.COMPLETED.value, errors_json=errors)
        self.session.add(run)
        if commit:
            for row in valid:
                self.session.add(SuppressionList(email=row["value"] if row["type"] == "email" else None, domain=row["value"] if row["type"] == "domain" else None, reason=SuppressionReason(row["reason"]), source="phase10_import"))
            run.imported_rows = len(valid)
        self.session.commit()
        return run
