from app.core.enums import EmailSendQueueStatus
from app.services.send_queue_service import SendQueueService
from tests.phase10_helpers import make_phase10_queue_item, send_settings


def test_only_phase9_ready_items_enter_send_queue(session):
    _, run, item, _ = make_phase10_queue_item(session)
    assert run.queued_count == 1
    assert item.queue_status == EmailSendQueueStatus.READY_TO_SEND_CONTROLLED


def test_queue_build_idempotent_and_key_stable(session):
    campaign, _, item, settings = make_phase10_queue_item(session)
    key = item.idempotency_key
    SendQueueService(session, settings).build_queue(campaign.slug, None, commit=True)
    assert item.idempotency_key == key
    assert session.query(type(item)).count() == 1


def test_provider_config_gaps_block_queue(session):
    _, run, item, _ = make_phase10_queue_item(session, send_settings(smtp_host="", smtp_username="", smtp_password=""))
    assert run.queued_count == 0
    assert item.queue_status == EmailSendQueueStatus.BLOCKED_BY_PROVIDER_CONFIG
