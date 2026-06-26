from pathlib import Path

from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
from app.services.phase8_report_service import Phase8ReportService
from app.settings import Settings
from tests.phase8_helpers import make_judge_pending_draft


def test_phase8_reports_generated(session, tmp_path):
    campaign, generation_run, _ = make_judge_pending_draft(session)
    run = EmailJudgeOrchestratorService(session, Settings()).judge_emails(campaign.slug, generation_run.run_id, commit=True)
    md, json_path, human_csv, rewrite_csv, blocked_csv, report = Phase8ReportService(session).write(run, Path(tmp_path))
    assert md.exists()
    assert json_path.exists()
    assert human_csv.exists()
    assert rewrite_csv.exists()
    assert blocked_csv.exists()
    assert "No email was sent" in md.read_text()
    assert report["judge_mode"] == "RULE_ONLY"
    assert "top_blocker_reasons" in report
