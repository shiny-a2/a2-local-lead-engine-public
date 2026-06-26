from app.core.enums import ContactStatus, EmailType
from app.db.models.candidate_contact_verification import CandidateContactVerification


class ComplianceScoringService:
    def score(self, contact: CandidateContactVerification | None, unresolved_reviews: int) -> dict[str, object]:
        score = 80.0
        warnings: list[str] = []
        blocker = False
        if contact is None:
            score = 45.0
            warnings.append("no_contact_verification")
        else:
            if contact.contact_status == ContactStatus.PERSONAL_EMAIL_FOUND_BLOCKED:
                score = 0.0
                blocker = True
                warnings.append("personal_email_blocked")
            elif contact.manual_review_required:
                score -= 25
                warnings.append("contact_manual_review_required")
            if contact.best_email_type == EmailType.PERSONAL:
                score = 0.0
                blocker = True
                warnings.append("personal_email_type")
            if contact.contact_status in {ContactStatus.CONTACT_RISKY, ContactStatus.NEEDS_MANUAL_REVIEW}:
                score -= 35
                warnings.append("contact_risky_or_unclear")
        if unresolved_reviews:
            score -= min(40, unresolved_reviews * 15)
            warnings.append("unresolved_manual_review")
        return {"score": max(0.0, score), "blocker": blocker, "warnings": warnings}
