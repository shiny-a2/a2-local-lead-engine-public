from app.services.ops_readiness_service import OpsReadinessService
from tests.phase14_helpers import make_campaign


def test_ops_readiness_blocks_missing_sender_auth_and_unsubscribe(session, test_settings):
    campaign = make_campaign(session)
    checks = OpsReadinessService(session, test_settings).run(campaign.id)
    blocked = {check.check_name for check in checks if check.severity == "BLOCKER" and not check.passed}
    assert "dashboard_auth_configured" in blocked
    assert "sender_profile_config" in blocked
    assert "unsubscribe_config" in blocked
