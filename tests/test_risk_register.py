from app.db.models.pilot_audit_run import PilotAuditRun
from app.services.risk_register_service import RiskRegisterService
from tests.phase14_helpers import make_campaign


def test_risk_register_contains_phase15_boundary_risk(session):
    campaign = make_campaign(session)
    run = PilotAuditRun(run_id="r3", campaign_id=campaign.id, operation="audit", status="STARTED", dry_run=False)
    session.add(run)
    session.flush()
    rows = RiskRegisterService(session).create(run)
    assert any(row.risk_code == "RISK-P15" for row in rows)
