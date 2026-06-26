from app.services.spam_risk_judge_service import SpamRiskJudgeService
from tests.phase8_helpers import SAFE_BODY


def test_clickbait_subject_warned_or_blocked():
    score, flags = SpamRiskJudgeService().score("URGENT FREE MONEY GUARANTEED", SAFE_BODY)
    assert score > 30
    assert flags


def test_too_many_sales_words_blocked():
    score, flags = SpamRiskJudgeService().score("A simple idea", "Limited time free money guaranteed best price act now.")
    assert score > 30
    assert flags


def test_plain_text_passes():
    score, flags = SpamRiskJudgeService().score("A simple website idea", SAFE_BODY)
    assert score <= 30
    assert flags == []
