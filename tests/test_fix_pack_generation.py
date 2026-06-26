from app.db.models.pilot_audit_run import PilotAuditRun
from app.services.fix_pack_recommendation_service import FixPackRecommendationService
from tests.phase14_helpers import make_campaign


def test_fixpacks_include_phase14_and_phase15(session):
    campaign = make_campaign(session)
    run = PilotAuditRun(run_id="r4", campaign_id=campaign.id, operation="audit", status="STARTED", dry_run=False)
    session.add(run)
    session.flush()
    rows = FixPackRecommendationService(session).create(run)
    codes = {row.code for row in rows}
    assert {"FP-001", "FP-006"} <= codes
