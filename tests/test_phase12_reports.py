from pathlib import Path

from app.services.phase12_report_service import Phase12ReportService
from tests.phase12_helpers import build_opportunity_from_body


def test_phase12_reports_generated(session, tmp_path):
    build_opportunity_from_body(session, "how much is it?")
    paths = Phase12ReportService(session).write(Path(tmp_path))
    assert all(path.exists() for path in paths)
    text = paths[0].read_text(encoding="utf-8")
    assert "does not send replies" in text
    assert "does not quote prices automatically" in text
