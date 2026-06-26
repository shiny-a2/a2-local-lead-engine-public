from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.blocked_offer_claim import BlockedOfferClaim
from app.db.models.candidate_business_insight import CandidateBusinessInsight
from app.db.models.candidate_economic_value_angle import CandidateEconomicValueAngle
from app.db.models.candidate_offer_match import CandidateOfferMatch
from app.db.models.future_email_offer_block import FutureEmailOfferBlock
from app.db.models.implementation_feasibility_note import ImplementationFeasibilityNote
from app.db.models.offer_readiness_gate import OfferReadinessGate
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.db.models.price_positioning_recommendation import PricePositioningRecommendation


class OfferExplanationService:
    def __init__(self, session: Session):
        self.session = session

    def explain(self, candidate_id: int) -> dict[str, object]:
        phase5 = self.session.scalar(select(Phase5CandidateDecision).where(Phase5CandidateDecision.candidate_business_id == candidate_id).order_by(Phase5CandidateDecision.id.desc()))
        decision = self.session.scalar(select(Phase6CandidateDecision).where(Phase6CandidateDecision.candidate_business_id == candidate_id).order_by(Phase6CandidateDecision.id.desc()))
        offer = self.session.scalar(select(CandidateOfferMatch).where(CandidateOfferMatch.candidate_business_id == candidate_id).order_by(CandidateOfferMatch.id.desc()))
        insight = self.session.scalar(select(CandidateBusinessInsight).where(CandidateBusinessInsight.candidate_business_id == candidate_id).order_by(CandidateBusinessInsight.id.desc()))
        angles = self.session.scalars(select(CandidateEconomicValueAngle).where(CandidateEconomicValueAngle.candidate_business_id == candidate_id)).all()
        blocks = self.session.scalars(select(FutureEmailOfferBlock).where(FutureEmailOfferBlock.candidate_business_id == candidate_id)).all()
        claims = self.session.scalars(select(BlockedOfferClaim).where(BlockedOfferClaim.candidate_business_id == candidate_id)).all()
        notes = self.session.scalars(select(ImplementationFeasibilityNote).where(ImplementationFeasibilityNote.candidate_business_id == candidate_id)).all()
        gates = self.session.scalars(select(OfferReadinessGate).where(OfferReadinessGate.candidate_business_id == candidate_id)).all()
        price = self.session.scalar(select(PricePositioningRecommendation).where(PricePositioningRecommendation.candidate_business_id == candidate_id).order_by(PricePositioningRecommendation.id.desc()))
        return {
            "phase5_decision": phase5.decision.value if phase5 else None,
            "business_context": insight.business_context_summary if insight else None,
            "offer_package": offer.offer_package.value if offer else None,
            "selected_module_ids": offer.selected_module_ids_json if offer else [],
            "economic_value_angles": [row.angle_text for row in angles],
            "blocked_claims": [row.claim_text for row in claims],
            "future_email_block_count": len(blocks),
            "price_positioning": price.price_positioning.value if price else None,
            "implementation_feasibility": [row.feasibility_level.value for row in notes],
            "readiness_gates": [{"gate": row.gate_name.value, "passed": row.passed} for row in gates],
            "phase6_decision": decision.decision.value if decision else None,
        }
