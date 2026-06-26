from sqlalchemy.orm import Session

from app.db.models.fix_pack_recommendation import FixPackRecommendation


class FixPackRecommendationService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, audit_run) -> list[FixPackRecommendation]:
        data = [
            ("FP-001", "P0", "Phase14 governance implementation", "Phase14 was missing in the acceptance audit", [14], "No MVP closure gate", "Phase14 reports/dashboard/tests pass", "Implement governance audit, dashboard, reports, and gates."),
            ("FP-002", "P0", "DB/env/operator setup readiness", "Runtime config is not operator-ready", [1, 14], "Dry-runs cannot start", "doctor passes and env is redacted", "Configure DB/env and rerun readiness."),
            ("FP-003", "P0/P1", "Sender DNS unsubscribe configuration", "Sender and unsubscribe are empty", [10, 14], "Live send unsafe or blocked", "provider-check and unsubscribe config pass", "Configure cPanel/DNS/from/reply-to/unsubscribe secret."),
            ("FP-004", "P1", "Persian dashboard mojibake cleanup", "Some Persian labels are mojibake", [10, 11, 12, 13, 14], "Operator UX confusion", "Mojibake scan clean", "Re-save Persian route/template labels as UTF-8."),
            ("FP-005", "P1", "Dashboard auth hardening", "MVP auth is lightweight", [9, 10, 11, 12, 13, 14], "Private dashboard exposure", "Auth env configured and POST protection documented", "Harden auth before hosted use."),
            ("FP-006", "P1/P2", "Phase15 post-MVP country boundary", "Multi-country expansion is not implemented", [15], "False scale readiness claim", "Reports mark Phase15 POST_MVP or skeleton exists", "Keep Phase15 disabled/post-MVP for NZ tiny pilot."),
        ]
        rows = [
            FixPackRecommendation(
                pilot_audit_run_id=audit_run.id,
                code=code,
                priority=priority,
                title=title,
                root_cause=root,
                affected_phases_json=phases,
                risk_if_not_fixed=risk,
                acceptance_criteria=criteria,
                codex_ready_summary=summary,
            )
            for code, priority, title, root, phases, risk, criteria, summary in data
        ]
        self.session.add_all(rows)
        self.session.flush()
        return rows
