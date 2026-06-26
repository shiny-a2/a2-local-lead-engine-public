from pathlib import Path

from app.services.pilot_audit_service import PilotAuditService
from tests.phase14_helpers import make_campaign


def test_phase14_commit_creates_reports(session, test_settings, monkeypatch, tmp_path):
    campaign = make_campaign(session)
    monkeypatch.chdir(tmp_path)
    run, result = PilotAuditService(session, test_settings).run(campaign.slug, True)
    assert run.status in {"COMPLETED", "COMPLETED_WITH_WARNINGS"}
    assert Path(result["paths"]["md"]).exists()
    assert Path(result["paths"]["json"]).exists()
    assert Path(result["paths"]["mojibake"]).exists()
