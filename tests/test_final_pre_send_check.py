from app.core.enums import FinalPreSendCheckStatus, SuppressionReason
from app.db.models.suppression import SuppressionList
from app.services.final_pre_send_review_service import FinalPreSendReviewService
from app.services.manual_edit_service import ManualEditService
from tests.phase9_helpers import make_phase9_queue_item


def test_passes_safe_draft(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    check = FinalPreSendReviewService(session, settings).run(item.id)
    assert check.check_status in {FinalPreSendCheckStatus.PASSED, FinalPreSendCheckStatus.PASSED_WITH_WARNINGS}


def test_blocks_missing_sender_identity(session):
    _, _, _, item, settings = make_phase9_queue_item(session, sender=False)
    check = FinalPreSendReviewService(session, settings).run(item.id)
    assert check.check_status == FinalPreSendCheckStatus.FAILED
    assert "missing_sender_identity" in check.risk_flags_json


def test_blocks_missing_unsubscribe_and_unsafe_claim_and_multiple_cta(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    ManualEditService(session, settings).create_version(item.id, "Subject", "You don't have a website. Can we talk? Can we meet?", "Amirali", "Reason")
    check = FinalPreSendReviewService(session, settings).run(item.id)
    assert check.check_status == FinalPreSendCheckStatus.FAILED
    assert "unsafe_claim" in check.risk_flags_json


def test_blocks_suppressed_contact(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    session.add(SuppressionList(email="hello@example.com", reason=SuppressionReason.MANUAL_BLOCK, source="test"))
    session.flush()
    check = FinalPreSendReviewService(session, settings).run(item.id)
    assert check.suppression_ok is False
    assert check.check_status == FinalPreSendCheckStatus.FAILED
