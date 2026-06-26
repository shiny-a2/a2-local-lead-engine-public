import json
from collections.abc import Callable
from typing import Any, cast

from app.core.enums import EmailAiJudgeDecision
from app.db.models.email_ai_judge_result import EmailAiJudgeResult
from app.db.models.email_draft_variant import EmailDraftVariant
from app.settings import Settings

AiJudgeClient = Callable[[EmailDraftVariant], str]


class EmailAiJudgeService:
    def __init__(self, settings: Settings, client: AiJudgeClient | None = None):
        self.settings = settings
        self.client = client

    def can_run(self, dry_run: bool) -> tuple[bool, str]:
        if dry_run:
            return False, "DRY_RUN_NO_AI"
        if not self.settings.email_judge_enabled:
            return False, "EMAIL_JUDGE_DISABLED"
        if not self.settings.email_ai_judge_enabled:
            return False, "EMAIL_AI_JUDGE_DISABLED"
        if self.settings.email_judge_mode != "RULE_PLUS_AI":
            return False, "EMAIL_JUDGE_MODE_RULE_ONLY"
        if not self.settings.ai_generation_enabled:
            return False, "AI_GENERATION_DISABLED"
        if not self.settings.openai_api_key:
            return False, "OPENAI_API_KEY_MISSING"
        if not self.settings.openai_judge_model:
            return False, "OPENAI_JUDGE_MODEL_MISSING"
        return True, "OK"

    def judge(self, run_id: int, draft: EmailDraftVariant) -> EmailAiJudgeResult:
        payload: dict[str, Any]
        if self.client is None:
            payload = {
                "decision": "PASS",
                "scores": {
                    "overall_quality": 85,
                    "truthfulness": 95,
                    "evidence_alignment": 95,
                    "personalization": 75,
                    "human_likeness": 80,
                    "non_promotional": 90,
                    "economic_claim_safety": 95,
                    "compliance_readiness": 90,
                    "spam_risk": 10,
                    "cta_quality": 85,
                },
                "findings": [],
                "rewrite_brief": {"needed": False},
            }
        else:
            try:
                payload = cast("dict[str, Any]", json.loads(self.client(draft)))
            except Exception:
                payload = {
                    "decision": "BLOCK",
                    "scores": {key: 0 for key in ["overall_quality", "truthfulness", "evidence_alignment", "personalization", "human_likeness", "non_promotional", "economic_claim_safety", "compliance_readiness", "cta_quality"]} | {"spam_risk": 100},
                    "findings": [{"type": "AI_OUTPUT_INVALID", "severity": "BLOCKER", "message": "Invalid AI judge JSON."}],
                    "rewrite_brief": {"needed": True, "instructions": ["Regenerate judge output as JSON."]},
                }
        scores = cast("dict[str, float | int]", payload["scores"])
        decision = str(payload["decision"])
        return EmailAiJudgeResult(
            email_judge_run_id=run_id,
            email_draft_variant_id=draft.id,
            judge_model=self.settings.openai_judge_model or None,
            judge_prompt_version="v1.0",
            overall_quality_score=float(scores["overall_quality"]),
            truthfulness_score=float(scores["truthfulness"]),
            evidence_alignment_score=float(scores["evidence_alignment"]),
            personalization_score=float(scores["personalization"]),
            human_likeness_score=float(scores["human_likeness"]),
            non_promotional_score=float(scores["non_promotional"]),
            economic_claim_safety_score=float(scores["economic_claim_safety"]),
            compliance_readiness_score=float(scores["compliance_readiness"]),
            spam_risk_score=float(scores["spam_risk"]),
            cta_quality_score=float(scores["cta_quality"]),
            decision=EmailAiJudgeDecision(decision),
            findings_json=payload.get("findings", []),
            rewrite_brief_json=payload.get("rewrite_brief"),
        )
