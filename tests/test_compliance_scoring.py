from app.core.enums import ContactStatus, EmailType
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.services.compliance_scoring_service import ComplianceScoringService
from tests.phase5_helpers import make_phase5_candidate


def test_high_compliance_risk_rejected_by_score(session):
    _, candidate = make_phase5_candidate(session, contact_status=ContactStatus.PERSONAL_EMAIL_FOUND_BLOCKED, email_type=EmailType.PERSONAL, contact_allowed=False)
    contact = session.query(CandidateContactVerification).filter_by(candidate_business_id=candidate.id).one()
    result = ComplianceScoringService().score(contact, unresolved_reviews=0)
    assert result["blocker"] is True


def test_contact_found_does_not_equal_final_permission(session):
    _, candidate = make_phase5_candidate(session, contact_status=ContactStatus.CONTACT_FORM_FOUND, email_type=EmailType.UNKNOWN, contact_allowed=False)
    contact = session.query(CandidateContactVerification).filter_by(candidate_business_id=candidate.id).one()
    result = ComplianceScoringService().score(contact, unresolved_reviews=0)
    assert contact.outreach_contact_allowed is False
    assert result["score"] < 80
