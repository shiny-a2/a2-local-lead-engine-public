from app.services.phase4_report_service import Phase4ReportService
from app.services.web_presence_decision_orchestrator import Phase4VerificationOrchestrator
from tests.test_candidate_quality import _candidate


def test_markdown_json_csv_reports_generated(session, test_settings, tmp_path):
    candidate = _candidate(session)
    candidate.status = "READY_FOR_WEBSITE_VERIFICATION"
    session.commit()
    run = Phase4VerificationOrchestrator(test_settings, session).full_review(5, commit=False)
    md_path, json_path, csv_path, report = Phase4ReportService(session).write(run, tmp_path)
    assert md_path.exists()
    assert json_path.exists()
    assert csv_path.exists()
    assert "does not authorize outreach" in md_path.read_text(encoding="utf-8")
    assert "final_verdict" in report
