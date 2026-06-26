from app.core.enums import Phase4WebsiteStatus
from app.db.models.candidate_lead_score import CandidateLeadScore
from app.services.lead_scoring_service import LeadScoringService
from app.services.scoring_profile_service import SCORE_VERSION, SCORING_PROFILE
from tests.phase5_helpers import make_phase5_candidate


def test_computes_score_components(session):
    campaign, _ = make_phase5_candidate(session)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    score = session.query(CandidateLeadScore).filter_by(scoring_run_id=run.id).one()
    assert score.website_opportunity_score == 85
    assert score.business_fit_score == 90
    assert score.score_version == SCORE_VERSION
    assert score.scoring_profile == SCORING_PROFILE


def test_strong_no_website_candidate_gets_high_score(session):
    campaign, _ = make_phase5_candidate(session, website_status=Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    score = session.query(CandidateLeadScore).filter_by(scoring_run_id=run.id).one()
    assert score.overall_lead_score >= 80


def test_social_only_candidate_scores_well(session):
    campaign, _ = make_phase5_candidate(session, website_status=Phase4WebsiteStatus.SOCIAL_ONLY)
    run = LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    score = session.query(CandidateLeadScore).filter_by(scoring_run_id=run.id).one()
    assert score.website_opportunity_score == 80
