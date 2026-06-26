from pathlib import Path

from app.services.suppression_import_service import SuppressionImportService


def test_suppression_import_dry_run_and_commit(session, tmp_path):
    path = Path(tmp_path) / "s.csv"
    path.write_text("type,value,reason\nemail,a@example.com,MANUAL_BLOCK\ndomain,example.com,LEGAL_RISK\n", encoding="utf-8")
    dry = SuppressionImportService(session).run(path, commit=False)
    assert dry.imported_rows == 0
    run = SuppressionImportService(session).run(path, commit=True)
    assert run.imported_rows == 2
