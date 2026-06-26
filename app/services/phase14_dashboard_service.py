from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.fix_pack_recommendation import FixPackRecommendation
from app.db.models.ops_readiness_check import OpsReadinessCheck
from app.db.models.pilot_audit_run import PilotAuditRun
from app.db.models.risk_register_item import RiskRegisterItem


class Phase14DashboardService:
    def __init__(self, session: Session):
        self.session = session

    def dashboard(self) -> dict:
        runs = self.session.scalars(select(PilotAuditRun).order_by(PilotAuditRun.id.desc())).all()
        risks = self.session.scalars(select(RiskRegisterItem)).all()
        fixes = self.session.scalars(select(FixPackRecommendation)).all()
        checks = self.session.scalars(select(OpsReadinessCheck)).all()
        return {
            "runs": len(runs),
            "latest_run": runs[0].run_id if runs else None,
            "risks": len(risks),
            "fixpacks": len(fixes),
            "ops_blockers": sum(1 for check in checks if check.severity == "BLOCKER" and not check.passed),
            "no_outbound": True,
        }
