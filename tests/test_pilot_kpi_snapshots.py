from app.db.models.pilot_audit_run import PilotAuditRun
from app.services.pilot_kpi_snapshot_service import PilotKpiSnapshotService
from tests.phase14_helpers import make_campaign


def test_kpi_snapshots_created(session):
    campaign = make_campaign(session)
    run = PilotAuditRun(run_id="r1", campaign_id=campaign.id, operation="audit", status="STARTED", dry_run=False)
    session.add(run)
    session.flush()
    rows = PilotKpiSnapshotService(session).create(run)
    assert any(row.metric_name == "candidates" for row in rows)
