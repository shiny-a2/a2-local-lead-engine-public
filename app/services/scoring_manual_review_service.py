from typing import cast

from app.core.enums import GateSeverity, ManualReviewStatus, ReadinessGateName, ScoringReviewType
from app.db.models.scoring_manual_review_item import ScoringManualReviewItem


class ScoringManualReviewService:
    def create_for_failures(self, candidate_id: int, scoring_run_id: int, gates: list[dict[str, object]]) -> list[ScoringManualReviewItem]:
        items: list[ScoringManualReviewItem] = []
        mapping = {
            "claim_permission_gate": ScoringReviewType.CLAIM_PERMISSION_MISSING,
            "personalization_evidence_gate": ScoringReviewType.LOW_PERSONALIZATION_EVIDENCE,
            "safe_contact_gate": ScoringReviewType.CONTACT_PERMISSION_UNCLEAR,
            "compliance_safety_gate": ScoringReviewType.HIGH_COMPLIANCE_RISK,
            "campaign_scope_gate": ScoringReviewType.CAMPAIGN_FIT_AMBIGUOUS,
            "suppression_cooldown_gate": ScoringReviewType.SUPPRESSION_OR_COOLDOWN,
        }
        for gate in gates:
            name = cast(ReadinessGateName, gate["gate_name"]).value
            if gate["passed"] or name not in mapping:
                continue
            severity = cast(GateSeverity, gate["severity"])
            items.append(
                ScoringManualReviewItem(
                    candidate_business_id=candidate_id,
                    scoring_run_id=scoring_run_id,
                    review_type=mapping[name],
                    severity=severity.value,
                    reason=str(gate["reason"]),
                    recommended_action="Review before Phase 6; do not write or send outreach.",
                    evidence_json=gate.get("evidence_json", {}),
                    status=ManualReviewStatus.OPEN,
                )
            )
        return items
