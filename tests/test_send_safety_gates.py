from app.core.enums import EmailSendQueueStatus, SuppressionReason
from app.db.models.suppression import SuppressionList
from app.services.controlled_send_service import ControlledSendService
from tests.phase10_helpers import make_phase10_queue_item, send_once, send_settings


def test_disabled_send_flags_block_provider_call(session):
    campaign, _, item, settings = make_phase10_queue_item(session)
    run = ControlledSendService(session, settings).run(campaign.slug, 5, commit=True)
    assert run.blocked_count == 1
    assert item.queue_status == EmailSendQueueStatus.BLOCKED_BY_GLOBAL_KILL_SWITCH


def test_suppression_blocks_send(session):
    _, _, item, settings = make_phase10_queue_item(session)
    session.add(SuppressionList(email=item.recipient_email, reason=SuppressionReason.MANUAL_BLOCK, source="test"))
    session.commit()
    run = send_once(session, item, settings=send_settings(global_outreach_kill_switch=False, email_sending_enabled=True, controlled_send_enabled=True, provider_send_enabled=True))
    assert run.blocked_count == 1
    assert item.queue_status == EmailSendQueueStatus.BLOCKED_BY_SUPPRESSION


def test_daily_limit_blocks_send(session):
    _, _, item, _ = make_phase10_queue_item(session)
    settings = send_settings(global_outreach_kill_switch=False, email_sending_enabled=True, controlled_send_enabled=True, provider_send_enabled=True, send_daily_limit=0)
    run = send_once(session, item, settings=settings)
    assert run.blocked_count == 1
    assert item.queue_status == EmailSendQueueStatus.BLOCKED_BY_DAILY_LIMIT
