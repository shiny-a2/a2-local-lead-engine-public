from app.services.non_promotional_tone_service import NonPromotionalToneService
from tests.phase8_helpers import SAFE_BODY


def test_hype_words_warned_or_blocked():
    score, flags = NonPromotionalToneService().score("This amazing guaranteed offer is best in class.")
    assert score < 80
    assert flags


def test_fear_based_claims_blocked():
    score, flags = NonPromotionalToneService().score("You are losing customers and competitors are ahead.")
    assert score < 80
    assert flags


def test_calm_helpful_tone_passes():
    score, flags = NonPromotionalToneService().score(SAFE_BODY)
    assert score >= 80
    assert flags == []
