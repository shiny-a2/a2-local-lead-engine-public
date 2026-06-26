from app.core.enums import ContactStatus, Phase4Decision, Phase4WebsiteStatus


class WebPresenceDecisionService:
    def decide(self, website_status: Phase4WebsiteStatus, contact_status: ContactStatus) -> dict:
        if website_status == Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL:
            return {
                "decision": Phase4Decision.REJECT_WEBSITE_ALREADY_STRONG,
                "ready_for_phase5": False,
                "manual_review_required": False,
                "reject_reason": "Strong official website found for no-website MVP.",
                "confidence": 0.8,
            }
        if website_status in {Phase4WebsiteStatus.INSUFFICIENT_EVIDENCE, Phase4WebsiteStatus.NEEDS_MANUAL_REVIEW}:
            return {
                "decision": Phase4Decision.NEEDS_MANUAL_REVIEW,
                "ready_for_phase5": False,
                "manual_review_required": True,
                "reject_reason": None,
                "confidence": 0.5,
            }
        if contact_status in {ContactStatus.PERSONAL_EMAIL_FOUND_BLOCKED, ContactStatus.CONTACT_RISKY}:
            return {
                "decision": Phase4Decision.REJECT_COMPLIANCE_RISK,
                "ready_for_phase5": False,
                "manual_review_required": True,
                "reject_reason": "Contact compliance risk.",
                "confidence": 0.7,
            }
        return {
            "decision": Phase4Decision.READY_FOR_PHASE_5_SCORING,
            "ready_for_phase5": True,
            "manual_review_required": False,
            "reject_reason": None,
            "confidence": 0.75,
        }
