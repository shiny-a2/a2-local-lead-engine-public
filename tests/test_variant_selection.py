from app.core.enums import EmailJudgeDecisionValue
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.services.variant_selection_service import VariantSelectionService


def test_selects_highest_quality_passing_variant(session):
    session.add_all(
        [
            EmailJudgeDecision(email_judge_run_id=1, candidate_business_id=1, email_draft_variant_id=1, decision=EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW, quality_score=85),
            EmailJudgeDecision(email_judge_run_id=1, candidate_business_id=1, email_draft_variant_id=2, decision=EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW, quality_score=92),
        ]
    )
    session.flush()
    selection = VariantSelectionService(session).select_for_run(1)[0]
    assert selection.preferred_email_draft_variant_id == 2
    assert selection.backup_email_draft_variant_id == 1


def test_rejects_unsafe_variant_and_no_preferred_if_all_fail(session):
    session.add(EmailJudgeDecision(email_judge_run_id=2, candidate_business_id=1, email_draft_variant_id=1, decision=EmailJudgeDecisionValue.BLOCKED_COMPLIANCE_RISK, quality_score=20))
    session.flush()
    selection = VariantSelectionService(session).select_for_run(2)[0]
    assert selection.preferred_email_draft_variant_id is None
    assert selection.rejected_variant_ids_json == [1]
