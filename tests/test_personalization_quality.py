from app.services.personalization_quality_service import PersonalizationQualityService
from tests.phase8_helpers import SAFE_BODY


def test_generic_draft_blocked_or_low_score():
    score, flags = PersonalizationQualityService().score("Hi, I help businesses with websites.", anchor_count=0)
    assert score < 70
    assert "too_generic" in flags


def test_draft_with_two_anchors_passes():
    score, flags = PersonalizationQualityService().score(SAFE_BODY, anchor_count=2)
    assert score >= 70
    assert flags == []


def test_local_category_offer_anchors_recognized():
    score, _ = PersonalizationQualityService().score(SAFE_BODY, anchor_count=3)
    assert score > 80


def test_template_like_draft_warned():
    score, flags = PersonalizationQualityService().score("Dear business owner, I help local businesses with websites.", anchor_count=1)
    assert score < 70
    assert flags
