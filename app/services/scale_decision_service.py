from sqlalchemy.orm import Session

from app.db.models.scale_decision_record import ScaleDecisionRecord
from app.settings import Settings


class ScaleDecisionService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create(self, audit_run) -> ScaleDecisionRecord:
        sample_size = audit_run.sent_to_provider_count
        sample_ok = sample_size >= self.settings.phase14_min_sample_for_scale_decision
        if not sample_ok:
            decision = "PILOT_INCONCLUSIVE"
            reason = "Sample size is too low; scale readiness cannot be claimed."
        elif audit_run.blockers_count:
            decision = "NEEDS_FIX_PACK_BEFORE_SCALE"
            reason = "Governance or ops blockers remain."
        else:
            decision = "SCALE_READY_WITH_LIMITS"
            reason = "Pilot sample is sufficient and no blockers remain; scale only with limits."
        row = ScaleDecisionRecord(
            pilot_audit_run_id=audit_run.id,
            decision=decision,
            ready_for_scale=decision.startswith("SCALE_READY"),
            sample_size_ok=sample_ok,
            reason=reason,
            limits_json={"phase15": self.settings.phase15_boundary_status},
        )
        self.session.add(row)
        self.session.flush()
        return row
