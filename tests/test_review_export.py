from pathlib import Path

from app.services.phase9_report_service import Phase9ReportService
from app.services.review_pack_export_service import ReviewPackExportService
from tests.phase9_helpers import make_phase9_queue_item


def test_review_pack_exports_generated(session, tmp_path):
    _, _, run, _, _ = make_phase9_queue_item(session)
    md, csv_path, json_path = ReviewPackExportService(session).export(run, Path(tmp_path))
    assert md.exists()
    assert csv_path.exists()
    assert json_path.exists()


def test_phase9_report_exports_generated(session, tmp_path):
    _, _, run, _, _ = make_phase9_queue_item(session)
    md, approved, blocked, returned, report = Phase9ReportService(session).write(run, Path(tmp_path))
    assert md.exists()
    assert approved.exists()
    assert blocked.exists()
    assert returned.exists()
    assert report["final_verdict"]
