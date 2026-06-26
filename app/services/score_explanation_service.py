from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.campaign_fit_assessment import CampaignFitAssessment
from app.db.models.candidate_lead_score import CandidateLeadScore
from app.db.models.outreach_readiness_gate import OutreachReadinessGate
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision


class ScoreExplanationService:
    def __init__(self, session: Session):
        self.session = session

    def explain(self, candidate_id: int) -> dict[str, object]:
        score = self.session.scalar(
            select(CandidateLeadScore)
            .where(CandidateLeadScore.candidate_business_id == candidate_id)
            .order_by(CandidateLeadScore.id.desc())
        )
        decision = self.session.scalar(
            select(Phase5CandidateDecision)
            .where(Phase5CandidateDecision.candidate_business_id == candidate_id)
            .order_by(Phase5CandidateDecision.id.desc())
        )
        fit = self.session.scalar(
            select(CampaignFitAssessment)
            .where(CampaignFitAssessment.candidate_business_id == candidate_id)
            .order_by(CampaignFitAssessment.id.desc())
        )
        gates = self.session.scalars(
            select(OutreachReadinessGate).where(OutreachReadinessGate.candidate_business_id == candidate_id)
        ).all()
        return {
            "found": score is not None,
            "overall_lead_score": score.overall_lead_score if score else None,
            "components": score.score_reasons_json if score else {},
            "positive_reasons": score.positive_reasons_json if score else [],
            "negative_reasons": score.negative_reasons_json if score else [],
            "risk_flags": score.risk_flags_json if score else [],
            "campaign_lane": fit.campaign_lane.value if fit else None,
            "decision": decision.decision.value if decision else None,
            "priority_tier": decision.priority_tier.value if decision else None,
            "gates": [
                {"gate": row.gate_name.value, "passed": row.passed, "severity": row.severity.value, "reason": row.reason}
                for row in gates
            ],
            "recommended_next_action": "Use only as Phase 6 input; this is not outreach approval.",
        }
