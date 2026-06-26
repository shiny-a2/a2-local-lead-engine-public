from app.services.duplicate_send_guard_service import DuplicateSendGuardService
from tests.phase10_helpers import make_phase10_queue_item


def test_same_candidate_recipient_campaign_blocked(session):
    _, _, item, _ = make_phase10_queue_item(session)
    ok, reason = DuplicateSendGuardService(session).check(item.idempotency_key)
    assert ok is False
    assert reason == "duplicate_send"
