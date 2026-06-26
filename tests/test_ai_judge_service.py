import json

from app.core.enums import EmailAiJudgeDecision
from app.services.email_ai_judge_service import EmailAiJudgeService
from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
from app.settings import Settings
from tests.phase8_helpers import make_judge_pending_draft

VALID_AI = {
    "decision": "PASS",
    "scores": {
        "overall_quality": 91,
        "truthfulness": 95,
        "evidence_alignment": 94,
        "personalization": 80,
        "human_likeness": 82,
        "non_promotional": 90,
        "economic_claim_safety": 96,
        "compliance_readiness": 92,
        "spam_risk": 8,
        "cta_quality": 88,
    },
    "findings": [],
    "rewrite_brief": {"needed": False},
}


def test_dry_run_does_not_call_openai():
    assert EmailAiJudgeService(Settings()).can_run(dry_run=True) == (False, "DRY_RUN_NO_AI")


def test_ai_judge_disabled_blocks_ai_call():
    allowed, reason = EmailAiJudgeService(Settings(email_judge_enabled=True)).can_run(dry_run=False)
    assert allowed is False
    assert reason == "EMAIL_AI_JUDGE_DISABLED"


def test_missing_model_or_key_blocks_ai_call():
    settings = Settings(email_judge_enabled=True, email_ai_judge_enabled=True, email_judge_mode="RULE_PLUS_AI", ai_generation_enabled=True)
    allowed, reason = EmailAiJudgeService(settings).can_run(dry_run=False)
    assert allowed is False
    assert reason == "OPENAI_API_KEY_MISSING"


def test_mocked_valid_ai_judge_json_parses():
    settings = Settings(
        email_judge_enabled=True,
        email_ai_judge_enabled=True,
        email_judge_mode="RULE_PLUS_AI",
        ai_generation_enabled=True,
        openai_api_key="sk-test",
        openai_judge_model="judge-test",
    )
    result = EmailAiJudgeService(settings, lambda _draft: json.dumps(VALID_AI)).judge(1, make_simple_draft())
    assert result.decision == EmailAiJudgeDecision.PASS
    assert result.overall_quality_score == 91


def test_invalid_json_fails_safely():
    result = EmailAiJudgeService(Settings(openai_judge_model="judge-test"), lambda _draft: "not json").judge(1, make_simple_draft())
    assert result.decision == EmailAiJudgeDecision.BLOCK
    assert result.spam_risk_score == 100


def test_ai_pass_cannot_override_rule_blocker(session):
    campaign, generation_run, draft = make_judge_pending_draft(session)
    draft.body_text = "You don't have a website. I am Amirali. Would this help? {{unsubscribe_url}}"
    settings = Settings(
        email_judge_enabled=True,
        email_ai_judge_enabled=True,
        email_judge_mode="RULE_PLUS_AI",
        ai_generation_enabled=True,
        openai_api_key="sk-test",
        openai_judge_model="judge-test",
    )
    run = EmailJudgeOrchestratorService(session, settings, lambda _draft: json.dumps(VALID_AI)).judge_emails(
        campaign.slug,
        generation_run.run_id,
        commit=True,
    )
    assert run.blocked_count == 1


def make_simple_draft():
    from tests.phase8_helpers import draft

    return draft()
