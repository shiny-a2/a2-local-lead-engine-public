from app.services.personalization_readiness_service import PersonalizationReadinessService
from tests.phase5_helpers import make_phase5_candidate


def test_good_evidence_passes(session):
    _, candidate = make_phase5_candidate(session)
    result = PersonalizationReadinessService(session).evaluate(candidate.id)
    assert result["passed"] is True


def test_missing_claim_permission_prevents_phase6_readiness(session):
    _, candidate = make_phase5_candidate(session, claim=False)
    result = PersonalizationReadinessService(session).evaluate(candidate.id)
    assert result["passed"] is False


def test_missing_verified_evidence_lowers_score(session):
    _, candidate = make_phase5_candidate(session, evidence=False)
    result = PersonalizationReadinessService(session).evaluate(candidate.id)
    assert result["score"] < 50
