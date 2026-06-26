from app.db.models.pilot_audit_run import PilotAuditRun
from app.services.mvp_closure_gate_service import MVPClosureGateService
from app.services.ops_readiness_service import OpsReadinessService
from app.services.phase_readiness_audit_service import PhaseReadinessAuditService
from tests.phase14_helpers import make_campaign


def test_mvp_closure_with_ops_gaps_not_live_ready(session, test_settings):
    campaign = make_campaign(session)
    run = PilotAuditRun(run_id="r6", campaign_id=campaign.id, operation="audit", status="STARTED", dry_run=False)
    session.add(run)
    session.flush()
    phases = PhaseReadinessAuditService(session).create(run)
    checks = OpsReadinessService(session, test_settings).run(campaign.id, run.id)
    decision = MVPClosureGateService(session).create(run, checks, phases)
    assert decision.ready_for_live_pilot is False
    assert decision.decision in {"MVP_CLOSED_WITH_FIX_PACKS", "MVP_NOT_CLOSED_BLOCKED"}
