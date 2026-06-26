from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.pilot_audit_run import PilotAuditRun
from app.services.backup_export_service import BackupExportService
from app.services.final_pilot_report_service import FinalPilotReportService
from app.services.fix_pack_recommendation_service import FixPackRecommendationService
from app.services.mvp_closure_gate_service import MVPClosureGateService
from app.services.ops_readiness_service import OpsReadinessService
from app.services.phase_readiness_audit_service import PhaseReadinessAuditService
from app.services.pilot_funnel_analytics_service import PilotFunnelAnalyticsService
from app.services.pilot_kpi_snapshot_service import PilotKpiSnapshotService
from app.services.retention_policy_service import RetentionPolicyService
from app.services.risk_register_service import RiskRegisterService
from app.services.scale_decision_service import ScaleDecisionService
from app.settings import Settings


class PilotAuditService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def run(self, campaign_slug: str, commit: bool) -> tuple[PilotAuditRun, dict[str, object]]:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        funnel = PilotFunnelAnalyticsService(self.session).snapshot(campaign.id)
        run = PilotAuditRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation="phase14_full_governance_audit",
            status="DRY_RUN_ONLY" if not commit else "STARTED",
            dry_run=not commit,
            input_candidate_count=funnel["candidates"],
            sent_to_provider_count=funnel["sent_to_provider"],
            replies_count=funnel["inbound_messages"],
            opportunities_count=funnel["opportunities"],
            metadata_json={"phase15_boundary": self.settings.phase15_boundary_status},
        )
        self.session.add(run)
        self.session.flush()
        if commit:
            kpis = PilotKpiSnapshotService(self.session).create(run)
            phase_audits = PhaseReadinessAuditService(self.session).create(run)
            ops_checks = OpsReadinessService(self.session, self.settings).run(campaign.id, run.id)
            risks = RiskRegisterService(self.session).create(run, ops_checks)
            fixes = FixPackRecommendationService(self.session).create(run)
            RetentionPolicyService(self.session, self.settings).create(run.id)
            BackupExportService(self.session).record_manifest(run.id)
            ScaleDecisionService(self.session, self.settings).create(run)
            MVPClosureGateService(self.session).create(run, ops_checks, phase_audits)
            run.blockers_count = sum(1 for check in ops_checks if check.severity == "BLOCKER" and not check.passed)
            run.warnings_count = sum(1 for check in ops_checks if check.severity == "WARNING" and not check.passed)
            run.status = "COMPLETED_WITH_WARNINGS" if run.blockers_count or run.warnings_count else "COMPLETED"
            payload: dict[str, object] = {
                "kpis": len(kpis),
                "phase_audits": len(phase_audits),
                "risks": len(risks),
                "fixpacks": len(fixes),
            }
        else:
            payload = {"dry_run": True, "would_create_reports": True, "funnel": funnel}
        run.finished_at = datetime.now(UTC)
        self.session.flush()
        paths = FinalPilotReportService(self.session).write(run) if commit else {}
        return run, {"funnel": funnel, "paths": {key: str(value) for key, value in paths.items()}, **payload}
