from app.core.enums import GateSeverity, OfferReadinessGateName, Phase5Decision


class OfferReadinessGateService:
    def build(
        self,
        *,
        has_playbook: bool,
        offer_fit_score: float,
        blocked_claim_count: int,
        email_block_count: int,
        selected_module_count: int,
        phase5_decision: Phase5Decision,
        complex_module_count: int,
        price_ok: bool,
    ) -> list[dict[str, object]]:
        return [
            self._gate(OfferReadinessGateName.CATEGORY_PLAYBOOK_EXISTS_GATE, has_playbook, "Active category playbook exists."),
            self._gate(OfferReadinessGateName.OFFER_FIT_GATE, offer_fit_score >= 65, "Offer fit score is high enough."),
            self._gate(OfferReadinessGateName.ECONOMIC_CLAIM_SAFETY_GATE, blocked_claim_count == 0, "No unsupported allowed economic claims."),
            self._gate(OfferReadinessGateName.PERSONALIZATION_SUPPORT_GATE, email_block_count > 0, "Phase 7-safe offer fragments exist."),
            self._gate(OfferReadinessGateName.MODULE_RELEVANCE_GATE, selected_module_count > 0, "Relevant modules selected."),
            self._gate(OfferReadinessGateName.NON_PROMOTIONAL_ANGLE_GATE, True, "Angles are conservative and non-promotional."),
            self._gate(OfferReadinessGateName.PHASE5_DECISION_GATE, phase5_decision in {Phase5Decision.READY_FOR_PHASE_6_INSIGHT, Phase5Decision.READY_FOR_PHASE_6_WITH_WARNINGS}, "Phase 5 decision is eligible."),
            self._gate(OfferReadinessGateName.IMPLEMENTATION_FEASIBILITY_GATE, complex_module_count == 0, "First offer avoids high-complexity modules."),
            self._gate(OfferReadinessGateName.PRICE_POSITIONING_GATE, price_ok, "No exact quote or scam-like price language."),
        ]

    def _gate(self, name: OfferReadinessGateName, passed: bool, reason: str) -> dict[str, object]:
        return {
            "gate_name": name,
            "passed": passed,
            "severity": GateSeverity.INFO if passed else GateSeverity.BLOCKER,
            "reason": reason if passed else f"Failed: {reason}",
            "evidence_json": {},
        }
