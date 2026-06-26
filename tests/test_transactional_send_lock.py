from app.core.enums import EmailSendQueueStatus
from app.services.transactional_send_lock_service import TransactionalSendLockService
from tests.phase10_helpers import make_phase10_queue_item, send_once


def test_concurrent_claim_prevented(session):
    _, _, item, _ = make_phase10_queue_item(session)
    assert TransactionalSendLockService(session).claim(item) is True
    assert TransactionalSendLockService(session).claim(item) is False


def test_sent_item_cannot_resend(session):
    _, _, item, _ = make_phase10_queue_item(session)
    send_once(session, item)
    assert item.queue_status == EmailSendQueueStatus.SENT_TO_PROVIDER
    assert TransactionalSendLockService(session).claim(item) is False
