from app.services.business_insight_orchestrator_service import BusinessInsightOrchestratorService
from app.services.phase6_report_service import Phase6ReportService
from tests.phase6_helpers import make_phase6_ready_candidate


def test_phase6_reports_generated(session, tmp_path):
    campaign, _ = make_phase6_ready_candidate(session)
    run = BusinessInsightOrchestratorService(session).run(campaign.slug, commit=True)
    md_path, json_path, blocks_path, manual_path, report = Phase6ReportService(session).write(run, tmp_path)
    assert md_path.exists()
    assert json_path.exists()
    assert blocks_path.exists()
    assert manual_path.exists()
    assert "does not write emails" in md_path.read_text(encoding="utf-8")
    assert report["blocked_claims_count"] >= 1
    assert report["future_email_offer_block_count"] >= 1
