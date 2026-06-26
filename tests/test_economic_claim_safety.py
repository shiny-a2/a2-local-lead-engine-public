from app.services.economic_claim_judge_service import EconomicClaimJudgeService


def test_safe_economic_angles_allowed():
    service = EconomicClaimJudgeService()
    for text in ["direct booking path", "reduce reliance where it matters", "owned menu page", "direct quote requests"]:
        score, flags = service.score(text)
        assert score >= 90
        assert flags == []


def test_unsafe_economic_claims_blocked():
    service = EconomicClaimJudgeService()
    for text in ["stop paying commissions", "guaranteed bookings", "save thousands", "replace all platforms"]:
        score, flags = service.score(text)
        assert score < 90
        assert flags
