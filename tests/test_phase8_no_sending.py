from app.core.enums import EmailJudgeDecisionValue
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.email_send import EmailSend
from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
from app.settings import Settings
from tests.phase8_helpers import make_judge_pending_draft


def test_phase8_creates_no_sending_or_send_ready_status(session):
    campaign, generation_run, _ = make_judge_pending_draft(session)
    run = EmailJudgeOrchestratorService(session, Settings()).judge_emails(campaign.slug, generation_run.run_id, commit=True)
    decisions = {row.decision for row in session.query(EmailJudgeDecision).all()}
    assert run.input_draft_count == 1
    assert session.query(EmailSend).count() == 0
    assert decisions & {
        EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW,
        EmailJudgeDecisionValue.APPROVED_WITH_WARNINGS_FOR_HUMAN_REVIEW,
    }
    assert all("SEND" not in decision.value and "OUTREACH" not in decision.value for decision in decisions)
