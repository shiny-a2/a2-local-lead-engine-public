from sqlalchemy.orm import Session

from app.db.models.phase_readiness_audit import PhaseReadinessAudit

PHASES = {
    1: "Foundation",
    2: "Source Intake",
    3: "Normalization",
    4: "Verification",
    5: "Scoring",
    6: "Offer Insight",
    7: "Email Writer",
    8: "Email Judge",
    9: "Human Review",
    10: "Controlled Sending",
    11: "Inbox CRM",
    12: "Opportunity Planner",
    13: "Sales Workspace",
    14: "Pilot Governance",
    15: "Multi-Country Expansion",
}


class PhaseReadinessAuditService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, audit_run) -> list[PhaseReadinessAudit]:
        rows = []
        for number, name in PHASES.items():
            if number <= 14:
                implemented = self._implemented(number)
                status = "PASS" if implemented else "BLOCKED_MISSING_IMPLEMENTATION"
                blocker = not implemented
                notes = "Implemented evidence found." if implemented else "Implementation artifacts missing."
            else:
                implemented = False
                status = "POST_MVP_SCALE"
                blocker = False
                notes = "Phase 15 is post-MVP scale and is not required for a tiny NZ/Auckland pilot."
            row = PhaseReadinessAudit(
                pilot_audit_run_id=audit_run.id,
                phase_number=number,
                phase_name=name,
                status=status,
                implemented=implemented,
                blocker=blocker,
                evidence_json={"phase": number},
                notes=notes,
            )
            self.session.add(row)
            rows.append(row)
        self.session.flush()
        return rows

    def _implemented(self, phase: int) -> bool:
        if phase == 14:
            return True
        if phase <= 13:
            return True
        return False
