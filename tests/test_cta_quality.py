from app.services.cta_quality_judge_service import CtaQualityJudgeService


def test_single_soft_cta_passes():
    score, flags = CtaQualityJudgeService().score("Would a quick idea be useful?")
    assert score >= 80
    assert flags == []


def test_multiple_ctas_blocked():
    score, flags = CtaQualityJudgeService().score("Can we talk? Want a quote?")
    assert score < 80
    assert "multiple_cta" in flags


def test_urgent_cta_blocked():
    score, flags = CtaQualityJudgeService().score("Book a call now before this limited offer ends.")
    assert score < 80
    assert flags
