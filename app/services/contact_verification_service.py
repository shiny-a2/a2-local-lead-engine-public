from sqlalchemy.orm import Session

from app.core.enums import ContactStatus, EmailType
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.contact_candidate import ContactCandidate


class ContactVerificationService:
    def __init__(self, session: Session | None = None):
        self.session = session

    def summarize(
        self, candidate_id: int, verification_run_id: int, contacts: list[ContactCandidate]
    ) -> CandidateContactVerification:
        allowed = [item for item in contacts if item.allowed_for_outreach and item.contact_type.value == "email"]
        personal = [item for item in contacts if item.blocked_reason and "PERSONAL" in item.blocked_reason]
        if allowed:
            best = allowed[0]
            status = ContactStatus.ROLE_BASED_EMAIL_FOUND
            email_type = EmailType.ROLE_BASED
            reason = "Low-risk generic or role email candidate found; not final sending permission."
        elif personal:
            best = personal[0]
            status = ContactStatus.PERSONAL_EMAIL_FOUND_BLOCKED
            email_type = EmailType.PERSONAL
            reason = "Personal-looking email blocked."
        elif contacts:
            best = contacts[0]
            status = ContactStatus.NEEDS_MANUAL_REVIEW
            email_type = EmailType.UNKNOWN
            reason = "Contact evidence exists but requires review."
        else:
            best = None
            status = ContactStatus.NO_CONTACT_FOUND
            email_type = None
            reason = "No contact candidate found."
        row = CandidateContactVerification(
            candidate_business_id=candidate_id,
            verification_run_id=verification_run_id,
            best_email=best.contact_value if best and best.contact_type.value == "email" else None,
            best_email_type=email_type,
            best_email_confidence=best.confidence if best else None,
            best_contact_url=best.contact_source_url if best else None,
            contact_status=status,
            outreach_contact_allowed=bool(allowed),
            manual_review_required=not bool(allowed),
            decision_reason=reason,
            evidence_json={"contact_found_not_sending_permission": True},
        )
        if self.session is not None:
            self.session.add(row)
            self.session.commit()
            self.session.refresh(row)
        return row

