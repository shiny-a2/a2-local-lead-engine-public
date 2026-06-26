from app.core.enums import EmailAiJudgeDecision, JudgeDisagreementResolution
from app.services.judge_disagreement_service import JudgeDisagreementService


def test_rule_blocker_overrides_ai_pass():
    row = JudgeDisagreementService().resolve(1, 1, False, EmailAiJudgeDecision.PASS)
    assert row is not None
    assert row.final_resolution == JudgeDisagreementResolution.RULE_BLOCKER_OVERRIDES


def test_ai_rewrite_triggers_rewrite_decision():
    row = JudgeDisagreementService().resolve(1, 1, True, EmailAiJudgeDecision.REWRITE_REQUIRED)
    assert row is not None
    assert row.final_resolution == JudgeDisagreementResolution.AI_REWRITE_ACCEPTED


def test_minor_agreement_creates_no_disagreement():
    assert JudgeDisagreementService().resolve(1, 1, True, EmailAiJudgeDecision.PASS_WITH_WARNINGS) is None
