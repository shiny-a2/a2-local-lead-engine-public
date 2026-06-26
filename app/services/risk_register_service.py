from sqlalchemy.orm import Session

from app.db.models.risk_register_item import RiskRegisterItem


class RiskRegisterService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, audit_run, ops_checks: list | None = None) -> list[RiskRegisterItem]:
        checks = ops_checks or []
        rows_data = [
            ("RISK-DB", "CRITICAL", "Database readiness", [1, 14], "DB/env may be unavailable", "Run doctor and migrations before dry-run"),
            ("RISK-SENDER", "CRITICAL", "Sender and unsubscribe readiness", [10, 14], "SMTP/DNS/unsubscribe may be missing", "Block live send until configured"),
            ("RISK-AUTH", "HIGH", "Dashboard auth hardening", [9, 10, 11, 12, 13, 14], "MVP auth is lightweight", "Configure credentials and harden before hosted use"),
            ("RISK-P15", "MEDIUM", "Phase 15 post-MVP boundary", [15], "Multi-country gates are not implemented", "Keep Phase 15 post-MVP or implement skeleton"),
        ]
        if any(check.severity == "BLOCKER" for check in checks):
            rows_data.append(("RISK-OPS", "CRITICAL", "Operator setup incomplete", [14], "Ops checks have blockers", "Complete operator checklist"))
        rows = [
            RiskRegisterItem(
                pilot_audit_run_id=audit_run.id,
                risk_code=code,
                severity=severity,
                title=title,
                affected_phases_json=phases,
                root_cause=root,
                mitigation=mitigation,
                status="OPEN",
                evidence_json={"phase14": True},
            )
            for code, severity, title, phases, root, mitigation in rows_data
        ]
        self.session.add_all(rows)
        self.session.flush()
        return rows
