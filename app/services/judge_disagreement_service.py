from app.core.enums import EmailAiJudgeDecision, JudgeDisagreementResolution
from app.db.models.email_judge_disagreement import EmailJudgeDisagreement


class JudgeDisagreementService:
    def resolve(self, run_id: int, draft_id: int, rule_passed: bool, ai_decision: EmailAiJudgeDecision | None) -> EmailJudgeDisagreement | None:
        if rule_passed and ai_decision in {None, EmailAiJudgeDecision.PASS, EmailAiJudgeDecision.PASS_WITH_WARNINGS}:
            return None
        if not rule_passed and ai_decision in {EmailAiJudgeDecision.PASS, EmailAiJudgeDecision.PASS_WITH_WARNINGS}:
            return EmailJudgeDisagreement(
                email_judge_run_id=run_id,
                email_draft_variant_id=draft_id,
                rule_decision="BLOCK",
                ai_decision=ai_decision.value,
                final_resolution=JudgeDisagreementResolution.RULE_BLOCKER_OVERRIDES,
                reason="Rule blocker overrides AI pass.",
            )
        if ai_decision == EmailAiJudgeDecision.REWRITE_REQUIRED:
            return EmailJudgeDisagreement(
                email_judge_run_id=run_id,
                email_draft_variant_id=draft_id,
                rule_decision="PASS" if rule_passed else "BLOCK",
                ai_decision=ai_decision.value,
                final_resolution=JudgeDisagreementResolution.AI_REWRITE_ACCEPTED,
                reason="AI requested rewrite guidance.",
            )
        return None
