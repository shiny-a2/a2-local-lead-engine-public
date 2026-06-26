from pathlib import Path

from app.services.phase11_report_service import Phase11ReportService
from tests.phase11_helpers import import_message


def test_reports_generated(session, tmp_path):
    run, _ = import_message(session)
    paths = Phase11ReportService(session).write(run, Path(tmp_path))
    assert all(path.exists() for path in paths)
    assert "does not send replies" in paths[0].read_text(encoding="utf-8")
