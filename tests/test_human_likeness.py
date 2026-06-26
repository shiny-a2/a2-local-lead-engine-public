from app.services.human_likeness_judge_service import HumanLikenessJudgeService
from tests.phase8_helpers import SAFE_BODY


def test_agency_like_draft_warned_or_blocked():
    score, flags = HumanLikenessJudgeService().score("Our agency provides a comprehensive end-to-end digital transformation solution.")
    assert score < 70
    assert flags


def test_salesy_draft_blocked():
    score, flags = HumanLikenessJudgeService().score("Limited time offer! Best price today only!")
    assert score < 70
    assert flags


def test_plain_human_draft_passes():
    score, flags = HumanLikenessJudgeService().score(SAFE_BODY)
    assert score >= 70
    assert flags == []
