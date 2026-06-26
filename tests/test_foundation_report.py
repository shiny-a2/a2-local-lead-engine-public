import json

from app.core.run_context import RunContext
from app.services.report_service import build_foundation_report, write_foundation_report


def test_foundation_report_files_are_generated(session, test_settings, tmp_path):
    report = build_foundation_report(test_settings, session, RunContext(run_id="run-report"))
    md_path, json_path = write_foundation_report(report, tmp_path)
    assert md_path.exists()
    assert json_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["final_verdict"] == "FOUNDATION_READY_FOR_PHASE_2_CONNECTORS"


def test_foundation_report_marks_risky_operations_disabled(session, test_settings):
    report = build_foundation_report(test_settings, session, RunContext(run_id="run-report"))
    assert report["external_api_status"] == "disabled/not-called"
    assert report["email_sending"] == "disabled"
    assert report["voice_calls"] == "disabled"
    assert report["google_maps"] == "disabled/prohibited for MVP"

