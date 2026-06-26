from typing import cast

from app.core.enums import GateSeverity, ManualReviewStatus, OfferReadinessGateName, OfferReviewType
from app.db.models.offer_manual_review_item import OfferManualReviewItem


class Phase6ManualReviewService:
    mapping = {
        "category_playbook_exists_gate": OfferReviewType.MISSING_PLAYBOOK,
        "offer_fit_gate": OfferReviewType.LOW_OFFER_FIT,
        "economic_claim_safety_gate": OfferReviewType.UNSUPPORTED_ECONOMIC_CLAIM,
        "personalization_support_gate": OfferReviewType.INSUFFICIENT_PERSONALIZATION_SUPPORT,
        "module_relevance_gate": OfferReviewType.MODULE_RELEVANCE_CONFLICT,
        "implementation_feasibility_gate": OfferReviewType.IMPLEMENTATION_RISK,
        "price_positioning_gate": OfferReviewType.PRICE_POSITIONING_RISK,
    }

    def create(self, candidate_id: int, insight_run_id: int, gates: list[dict[str, object]]) -> list[OfferManualReviewItem]:
        items: list[OfferManualReviewItem] = []
        for gate in gates:
            name = cast(OfferReadinessGateName, gate["gate_name"]).value
            if gate["passed"] or name not in self.mapping:
                continue
            severity = cast(GateSeverity, gate["severity"])
            items.append(
                OfferManualReviewItem(
                    candidate_business_id=candidate_id,
                    insight_run_id=insight_run_id,
                    review_type=self.mapping[name],
                    severity=severity.value,
                    reason=str(gate["reason"]),
                    recommended_action="Review offer ingredients before Phase 7; do not write email yet.",
                    evidence_json=gate.get("evidence_json", {}),
                    status=ManualReviewStatus.OPEN,
                )
            )
        return items
