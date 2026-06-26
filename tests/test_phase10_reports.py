from pathlib import Path

from app.services.phase10_report_service import Phase10ReportService
from tests.phase10_helpers import make_phase10_queue_item


def test_phase10_reports_generated(session, tmp_path):
    _, run, _, _ = make_phase10_queue_item(session)
    md, json_path, sent, blocked, errors, plan, report = Phase10ReportService(session).write(run, Path(tmp_path))
    assert md.exists()
    assert json_path.exists()
    assert sent.exists()
    assert blocked.exists()
    assert errors.exists()
    assert plan.exists()
    assert "cPanel SMTP acceptance" in md.read_text()
    assert report["safety_summary"]["followup_automation"] is False
