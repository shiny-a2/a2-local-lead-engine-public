from app.core.enums import ContactStatus, EmailType, Phase5Decision
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision as DecisionModel
from app.services.lead_scoring_service import LeadScoringService
from tests.phase5_helpers import make_phase5_candidate


def test_safe_contact_gate_passes_for_generic_email(session):
    campaign, _ = make_phase5_candidate(session)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    decision = session.query(DecisionModel).filter_by(scoring_run_id=run.id).one()
    assert decision.ready_for_phase6 is True


def test_personal_email_fails(session):
    campaign, _ = make_phase5_candidate(session, contact_status=ContactStatus.PERSONAL_EMAIL_FOUND_BLOCKED, email_type=EmailType.PERSONAL, contact_allowed=False)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    decision = session.query(DecisionModel).filter_by(scoring_run_id=run.id).one()
    assert decision.decision in {Phase5Decision.NEEDS_MANUAL_REVIEW, Phase5Decision.REJECT_HIGH_COMPLIANCE_RISK}


def test_claim_permission_missing_fails(session):
    campaign, _ = make_phase5_candidate(session, claim=False)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    decision = session.query(DecisionModel).filter_by(scoring_run_id=run.id).one()
    assert decision.ready_for_phase6 is False
