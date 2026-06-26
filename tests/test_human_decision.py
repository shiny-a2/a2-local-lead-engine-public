import pytest

from app.core.enums import HumanReviewQueueStatus
from app.db.models.email_send import EmailSend
from app.services.human_decision_service import HumanDecisionService
from tests.phase9_helpers import make_phase9_queue_item


def test_approve_creates_ready_for_phase10_only(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    decision = HumanDecisionService(session, settings).approve(item.id, "Amirali", "Looks good")
    assert "PHASE_10" in decision.decision.value
    assert session.query(EmailSend).count() == 0


def test_approve_fails_if_final_check_fails(session):
    _, _, _, item, settings = make_phase9_queue_item(session, sender=False)
    decision = HumanDecisionService(session, settings).approve(item.id, "Amirali", "Try")
    assert decision.decision.value == "BLOCKED_BY_FINAL_PRE_SEND_CHECK"


def test_reject_hold_return_rewrite_return_judge(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    service = HumanDecisionService(session, settings)
    assert service.reject(item.id, "Amirali", "No").decision.value == "REJECTED_BY_HUMAN"
    item.queue_status = HumanReviewQueueStatus.QUEUED
    assert service.hold(item.id, "Amirali", "Later").decision.value == "HOLD_FOR_LATER"
    item.queue_status = HumanReviewQueueStatus.QUEUED
    assert service.return_rewrite(item.id, "Amirali", "Rewrite").decision.value == "RETURN_TO_PHASE_7_REWRITE"
    item.queue_status = HumanReviewQueueStatus.QUEUED
    assert service.return_judge(item.id, "Amirali", "Rejudge").decision.value == "RETURN_TO_PHASE_8_REJUDGE"


def test_required_reasons_enforced(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    with pytest.raises(ValueError):
        HumanDecisionService(session, settings).reject(item.id, "Amirali", "")
