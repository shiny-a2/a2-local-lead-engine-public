from app.core.enums import EmailJudgeDecisionValue, HumanReviewQueueStatus
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.services.human_review_queue_service import HumanReviewQueueService
from app.settings import Settings
from tests.phase9_helpers import make_phase9_queue_item


def test_only_phase8_approved_drafts_enter_queue(session):
    campaign, judge_run, _, item, _ = make_phase9_queue_item(session)
    assert item.queue_status == HumanReviewQueueStatus.QUEUED
    assert HumanReviewQueueService(session, Settings()).eligible(judge_run.run_id)
    assert campaign.slug


def test_blocked_drafts_do_not_enter_queue(session):
    campaign, judge_run, _, item, _ = make_phase9_queue_item(session)
    decision = session.query(EmailJudgeDecision).first()
    decision.ready_for_phase9 = False
    decision.decision = EmailJudgeDecisionValue.BLOCKED_COMPLIANCE_RISK
    session.query(HumanReviewQueueItem).delete()
    session.commit()
    run = HumanReviewQueueService(session, Settings()).build_queue(campaign.slug, judge_run.run_id, commit=True)
    assert run.queued_count == 0


def test_queue_build_is_idempotent(session):
    campaign, judge_run, _, _, _ = make_phase9_queue_item(session)
    HumanReviewQueueService(session, Settings()).build_queue(campaign.slug, judge_run.run_id, commit=True)
    assert session.query(HumanReviewQueueItem).count() == 1
