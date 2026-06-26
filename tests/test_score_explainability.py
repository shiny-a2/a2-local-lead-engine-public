from app.services.lead_scoring_service import LeadScoringService
from app.services.score_explanation_service import ScoreExplanationService
from tests.phase5_helpers import make_phase5_candidate


def test_score_explanation_outputs_reasons_and_gates(session):
    campaign, candidate = make_phase5_candidate(session)
    LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    explanation = ScoreExplanationService(session).explain(candidate.id)
    assert explanation["found"] is True
    assert explanation["positive_reasons"]
    assert explanation["gates"]
    assert explanation["recommended_next_action"].startswith("Use only as Phase 6 input")
