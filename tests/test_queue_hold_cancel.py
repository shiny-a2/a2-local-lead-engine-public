from app.core.enums import EmailSendQueueStatus
from tests.phase10_helpers import make_phase10_queue_item


def test_held_and_cancelled_items_not_sendable(session):
    _, _, item, _ = make_phase10_queue_item(session)
    item.queue_status = EmailSendQueueStatus.HELD_BY_OPERATOR
    assert item.queue_status != EmailSendQueueStatus.READY_TO_SEND_CONTROLLED
    item.queue_status = EmailSendQueueStatus.CANCELLED_BY_OPERATOR
    assert item.queue_status != EmailSendQueueStatus.READY_TO_SEND_CONTROLLED
