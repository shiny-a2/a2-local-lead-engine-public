from sqlalchemy.orm import Session

from app.db.models.mvp_closure_decision import MvpClosureDecision


class MVPClosureGateService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, audit_run, ops_checks: list, phase_audits: list) -> MvpClosureDecision:
        ops_blockers = [check.check_name for check in ops_checks if check.severity == "BLOCKER" and not check.passed]
        phase_blockers = [row.phase_number for row in phase_audits if row.blocker and row.phase_number <= 14]
        if phase_blockers:
            decision = "MVP_NOT_CLOSED_BLOCKED"
            reason = f"Phase blockers remain: {phase_blockers}"
        elif ops_blockers:
            decision = "MVP_CLOSED_WITH_FIX_PACKS"
            reason = f"Operator setup/live readiness blockers remain: {ops_blockers}"
        elif audit_run.sent_to_provider_count < 1:
            decision = "MVP_INCONCLUSIVE_NEEDS_MORE_DATA"
            reason = "No live pilot sample exists; MVP closure is audit-ready but data-inconclusive."
        else:
            decision = "MVP_CLOSED_READY"
            reason = "No Phase 14 blockers remain."
        row = MvpClosureDecision(
            pilot_audit_run_id=audit_run.id,
            decision=decision,
            ready_for_operator_setup=decision != "MVP_NOT_CLOSED_BLOCKED",
            ready_for_controlled_dry_run=not phase_blockers and not ops_blockers,
            ready_for_live_pilot=decision == "MVP_CLOSED_READY",
            reason=reason,
            warnings_json=["Phase15 is post-MVP scale."] if decision != "MVP_CLOSED_READY" else [],
        )
        self.session.add(row)
        self.session.flush()
        return row
