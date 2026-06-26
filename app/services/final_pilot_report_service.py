import csv
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.fix_pack_recommendation import FixPackRecommendation
from app.db.models.mvp_closure_decision import MvpClosureDecision
from app.db.models.ops_readiness_check import OpsReadinessCheck
from app.db.models.phase_readiness_audit import PhaseReadinessAudit
from app.db.models.pilot_audit_run import PilotAuditRun
from app.db.models.pilot_kpi_snapshot import PilotKpiSnapshot
from app.db.models.risk_register_item import RiskRegisterItem
from app.db.models.scale_decision_record import ScaleDecisionRecord
from app.services.persian_mojibake_scan_service import PersianMojibakeScanService


class FinalPilotReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: PilotAuditRun) -> dict:
        kpis = self.session.scalars(select(PilotKpiSnapshot).where(PilotKpiSnapshot.pilot_audit_run_id == run.id)).all()
        risks = self.session.scalars(select(RiskRegisterItem).where(RiskRegisterItem.pilot_audit_run_id == run.id)).all()
        fixes = self.session.scalars(select(FixPackRecommendation).where(FixPackRecommendation.pilot_audit_run_id == run.id)).all()
        checks = self.session.scalars(select(OpsReadinessCheck).where(OpsReadinessCheck.pilot_audit_run_id == run.id)).all()
        phases = self.session.scalars(select(PhaseReadinessAudit).where(PhaseReadinessAudit.pilot_audit_run_id == run.id)).all()
        closure = self.session.scalar(select(MvpClosureDecision).where(MvpClosureDecision.pilot_audit_run_id == run.id))
        scale = self.session.scalar(select(ScaleDecisionRecord).where(ScaleDecisionRecord.pilot_audit_run_id == run.id))
        return {
            "run_id": run.run_id,
            "status": run.status,
            "dry_run": run.dry_run,
            "kpis": {row.metric_name: row.metric_value for row in kpis},
            "phase_readiness": {row.phase_number: row.status for row in phases},
            "risk_count": len(risks),
            "fixpack_count": len(fixes),
            "ops_blockers": [row.check_name for row in checks if row.severity == "BLOCKER" and not row.passed],
            "scale_decision": scale.decision if scale else "MISSING",
            "mvp_closure_decision": closure.decision if closure else "MISSING",
            "phase15_boundary": "POST_MVP_SCALE_NOT_REQUIRED_FOR_NZ_TINY_PILOT",
            "safety_summary": {
                "emails_sent": False,
                "smtp_called": False,
                "external_apis_called": False,
                "openai_called": False,
                "inbox_synced": False,
            },
            "final_verdict": closure.decision if closure else "MVP_NOT_CLOSED_BLOCKED",
        }

    def write(self, run: PilotAuditRun, out_dir: Path = Path("reports")) -> dict[str, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        report = self.build(run)
        paths = {
            "md": out_dir / f"phase14-pilot-final-{run.run_id}.md",
            "json": out_dir / f"phase14-pilot-final-{run.run_id}.json",
            "kpis": out_dir / f"phase14-funnel-kpis-{run.run_id}.csv",
            "risks": out_dir / f"phase14-risk-register-{run.run_id}.csv",
            "fixpacks": out_dir / f"phase14-fixpacks-{run.run_id}.csv",
            "scale": out_dir / f"phase14-scale-decision-{run.run_id}.md",
            "ops": out_dir / f"phase14-ops-readiness-{run.run_id}.md",
            "retention": out_dir / f"phase14-retention-policy-{run.run_id}.md",
            "mojibake": out_dir / f"phase14-persian-mojibake-scan-{run.run_id}.md",
        }
        paths["md"].write_text(self._markdown(report), encoding="utf-8")
        paths["json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._write_csv(paths["kpis"], ["metric", "value"], report["kpis"].items())
        risks = self.session.scalars(select(RiskRegisterItem).where(RiskRegisterItem.pilot_audit_run_id == run.id)).all()
        fixes = self.session.scalars(select(FixPackRecommendation).where(FixPackRecommendation.pilot_audit_run_id == run.id)).all()
        self._write_csv(paths["risks"], ["code", "severity", "title"], [[row.risk_code, row.severity, row.title] for row in risks])
        self._write_csv(paths["fixpacks"], ["code", "priority", "title"], [[row.code, row.priority, row.title] for row in fixes])
        paths["scale"].write_text(f"# Phase 14 Scale Decision\n\n{report['scale_decision']}\n", encoding="utf-8")
        paths["ops"].write_text(f"# Phase 14 Ops Readiness\n\nblockers: {report['ops_blockers']}\n", encoding="utf-8")
        paths["retention"].write_text("# Phase 14 Retention Policy\n\n.env files and secrets are excluded from exports.\n", encoding="utf-8")
        findings = PersianMojibakeScanService().scan()
        paths["mojibake"].write_text("# Phase 14 Persian Mojibake Scan\n\n" + json.dumps(findings, indent=2, sort_keys=True), encoding="utf-8")
        return paths

    def _write_csv(self, path: Path, headers: list[str], rows) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

    def _markdown(self, report: dict) -> str:
        return "\n".join(
            [
                "# Phase 14 MVP Closure Governance Report",
                "",
                "Phase 14 performs governance and readiness reporting only.",
                "No email was sent. SMTP was not called. External APIs were not called.",
                "OpenAI was not called. Inbox sync was not run.",
                "",
                f"run_id: {report['run_id']}",
                f"mvp_closure_decision: {report['mvp_closure_decision']}",
                f"scale_decision: {report['scale_decision']}",
                f"phase15_boundary: {report['phase15_boundary']}",
                f"ops_blockers: {report['ops_blockers']}",
                f"final_verdict: {report['final_verdict']}",
            ]
        )
