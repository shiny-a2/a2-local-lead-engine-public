from app.services.lead_scoring_service import LeadScoringService
from app.services.phase5_report_service import Phase5ReportService
from tests.phase5_helpers import make_phase5_candidate


def test_phase5_reports_generated(session, tmp_path):
    campaign, _ = make_phase5_candidate(session)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    md_path, json_path, pilot_path, manual_path, report = Phase5ReportService(session).write(run, tmp_path)
    assert md_path.exists()
    assert json_path.exists()
    assert pilot_path.exists()
    assert manual_path.exists()
    assert "does not generate emails" in md_path.read_text(encoding="utf-8")
    assert report["final_verdict"]
