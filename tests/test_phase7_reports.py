from app.services.email_writer_service import EmailWriterService
from app.services.phase7_report_service import Phase7ReportService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_phase7_reports_generated(session, tmp_path):
    campaign, _ = make_phase7_ready_candidate(session)
    run = EmailWriterService(session, Settings()).generate(campaign.slug, None, 10, commit=False)
    md_path, json_path, csv_path, report = Phase7ReportService(session).write(run, tmp_path)
    assert md_path.exists()
    assert json_path.exists()
    assert csv_path.exists()
    assert "No email was sent" in md_path.read_text(encoding="utf-8")
    assert report["openai_calls_attempted"] is False
