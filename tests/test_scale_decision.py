from app.db.models.pilot_audit_run import PilotAuditRun
from app.services.scale_decision_service import ScaleDecisionService
from tests.phase14_helpers import make_campaign


def test_low_sample_is_inconclusive(session, test_settings):
    campaign = make_campaign(session)
    run = PilotAuditRun(run_id="r5", campaign_id=campaign.id, operation="audit", status="STARTED", dry_run=False, sent_to_provider_count=0)
    session.add(run)
    session.flush()
    decision = ScaleDecisionService(session, test_settings).create(run)
    assert decision.decision == "PILOT_INCONCLUSIVE"
