from sqlalchemy.orm import Session

from app.db.models.pilot_kpi_snapshot import PilotKpiSnapshot
from app.services.pilot_funnel_analytics_service import PilotFunnelAnalyticsService


class PilotKpiSnapshotService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, audit_run) -> list[PilotKpiSnapshot]:
        metrics = PilotFunnelAnalyticsService(self.session).snapshot(audit_run.campaign_id)
        rows = [
            PilotKpiSnapshot(
                pilot_audit_run_id=audit_run.id,
                campaign_id=audit_run.campaign_id,
                metric_name=name,
                metric_value=value,
                metric_context_json={"source": "phase14_governance"},
            )
            for name, value in metrics.items()
        ]
        self.session.add_all(rows)
        self.session.flush()
        return rows
