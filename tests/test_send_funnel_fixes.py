"""Regression tests for the send-funnel unblock: the judge must advance a draft off
JUDGE_PENDING (else it re-judges the same drafts forever and starves the rest), and a second
judge run must then find nothing new to judge."""
from app.core.enums import EmailDraftVariantStatus
from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
from app.settings import Settings
from tests.phase8_helpers import make_judge_pending_draft


def test_judge_advances_draft_to_judged(session):
    campaign, generation_run, draft = make_judge_pending_draft(session)
    assert draft.status == EmailDraftVariantStatus.JUDGE_PENDING
    EmailJudgeOrchestratorService(session, Settings()).judge_emails(
        campaign.slug, generation_run.run_id, commit=True
    )
    session.refresh(draft)
    assert draft.status == EmailDraftVariantStatus.JUDGED


def test_second_judge_run_finds_no_pending_drafts(session):
    campaign, generation_run, _ = make_judge_pending_draft(session)
    svc = EmailJudgeOrchestratorService(session, Settings())
    svc.judge_emails(campaign.slug, generation_run.run_id, commit=True)
    # Nothing is left in JUDGE_PENDING, so a campaign-wide re-judge has zero input.
    run2 = svc.judge_emails(campaign.slug, None, commit=True)
    assert run2.input_draft_count == 0


def test_dry_run_judge_does_not_advance_status(session):
    # Dry runs must stay read-only so they don't silently consume drafts.
    campaign, generation_run, draft = make_judge_pending_draft(session)
    EmailJudgeOrchestratorService(session, Settings()).judge_emails(
        campaign.slug, generation_run.run_id, commit=False
    )
    session.refresh(draft)
    assert draft.status == EmailDraftVariantStatus.JUDGE_PENDING
