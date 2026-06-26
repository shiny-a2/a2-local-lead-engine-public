from app.db.models.pilot_audit_run import PilotAuditRun
from app.services.phase_readiness_audit_service import PhaseReadinessAuditService
from tests.phase14_helpers import make_campaign


def test_phase15_marked_post_mvp(session):
    campaign = make_campaign(session)
    run = PilotAuditRun(run_id="r2", campaign_id=campaign.id, operation="audit", status="STARTED", dry_run=False)
    session.add(run)
    session.flush()
    rows = PhaseReadinessAuditService(session).create(run)
    phase15 = next(row for row in rows if row.phase_number == 15)
    assert phase15.status == "POST_MVP_SCALE"
    assert phase15.blocker is False
