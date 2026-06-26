from app.core.enums import (
    CampaignLane,
    ContactStatus,
    GateSeverity,
    Phase4Decision,
    Phase4WebsiteStatus,
    ReadinessGateName,
)


class ReadinessGateService:
    def build(
        self,
        *,
        phase4_decision: Phase4Decision,
        website_status: Phase4WebsiteStatus,
        contact_status: ContactStatus,
        contact_allowed: bool,
        claim_permission_count: int,
        personalization_passed: bool,
        compliance_blocker: bool,
        unresolved_reviews: int,
        campaign_lane: CampaignLane,
        identity_confidence: float,
        suppressed: bool,
    ) -> list[dict[str, object]]:
        gates = [
            self._gate(
                ReadinessGateName.VERIFIED_WEB_PRESENCE_GATE,
                phase4_decision in {Phase4Decision.READY_FOR_PHASE_5_SCORING, Phase4Decision.READY_FOR_PHASE_5_WITH_WARNINGS}
                and website_status
                not in {Phase4WebsiteStatus.INSUFFICIENT_EVIDENCE, Phase4WebsiteStatus.NEEDS_MANUAL_REVIEW, Phase4WebsiteStatus.UNKNOWN},
                "Phase 4 decision and web presence evidence are eligible for scoring.",
            ),
            self._gate(
                ReadinessGateName.SAFE_CONTACT_GATE,
                contact_allowed or contact_status in {ContactStatus.CONTACT_FORM_FOUND, ContactStatus.SOCIAL_ONLY_CONTACT, ContactStatus.PHONE_ONLY},
                "Safe contact exists or warning-only contact policy applies for Phase 6 planning.",
                warning=True,
            ),
            self._gate(
                ReadinessGateName.CLAIM_PERMISSION_GATE,
                claim_permission_count > 0,
                "At least one conservative claim permission is available.",
            ),
            self._gate(
                ReadinessGateName.PERSONALIZATION_EVIDENCE_GATE,
                personalization_passed,
                "Verified future-copy evidence is sufficient.",
            ),
            self._gate(
                ReadinessGateName.COMPLIANCE_SAFETY_GATE,
                not compliance_blocker,
                "Compliance risk is acceptable for Phase 6 planning.",
            ),
            self._gate(
                ReadinessGateName.MANUAL_REVIEW_CLEAR_GATE,
                unresolved_reviews == 0,
                "No unresolved Phase 4 manual review blocker.",
            ),
            self._gate(
                ReadinessGateName.CAMPAIGN_SCOPE_GATE,
                campaign_lane in {CampaignLane.NO_WEBSITE, CampaignLane.SOCIAL_ONLY, CampaignLane.DIRECTORY_ONLY},
                "Candidate is in an MVP campaign lane.",
            ),
            self._gate(
                ReadinessGateName.IDENTITY_CONFIDENCE_GATE,
                identity_confidence >= 60,
                "Candidate identity confidence is high enough.",
            ),
            self._gate(
                ReadinessGateName.SUPPRESSION_COOLDOWN_GATE,
                not suppressed,
                "No suppression or cooldown hit found.",
            ),
        ]
        return gates

    def _gate(self, name: ReadinessGateName, passed: bool, reason: str, warning: bool = False) -> dict[str, object]:
        return {
            "gate_name": name,
            "passed": passed,
            "severity": GateSeverity.INFO if passed else GateSeverity.WARNING if warning else GateSeverity.BLOCKER,
            "reason": reason if passed else f"Failed: {reason}",
            "evidence_json": {},
        }
