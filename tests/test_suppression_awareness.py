from app.core.enums import SuppressionReason
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision as DecisionModel
from app.db.models.suppression import SuppressionList
from app.services.lead_scoring_service import LeadScoringService
from app.services.suppression_awareness_service import SuppressionAwarenessService
from tests.phase5_helpers import make_phase5_candidate


def test_no_suppression_safely_noops(session):
    assert SuppressionAwarenessService(session).check("hello@example.co.nz")["suppressed"] is False


def test_suppressed_email_blocks_readiness(session):
    campaign, candidate = make_phase5_candidate(session)
    contact = session.query(CandidateContactVerification).filter_by(candidate_business_id=candidate.id).one()
    session.add(SuppressionList(email=contact.best_email, reason=SuppressionReason.MANUAL_BLOCK, source="test"))
    session.commit()
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    decision = session.query(DecisionModel).filter_by(scoring_run_id=run.id).one()
    assert decision.ready_for_phase6 is False


def test_suppressed_domain_blocks_readiness(session):
    campaign, candidate = make_phase5_candidate(session)
    contact = session.query(CandidateContactVerification).filter_by(candidate_business_id=candidate.id).one()
    session.add(SuppressionList(domain=contact.best_email.split("@")[-1], reason=SuppressionReason.MANUAL_BLOCK, source="test"))
    session.commit()
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    decision = session.query(DecisionModel).filter_by(scoring_run_id=run.id).one()
    assert decision.ready_for_phase6 is False
