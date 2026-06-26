from app.core.enums import EmailSendQueueStatus
from app.services.controlled_send_service import ControlledSendService
from tests.phase10_helpers import make_phase10_queue_item, send_settings


def test_global_kill_switch_blocks_all_sends(session):
    campaign, _, item, _ = make_phase10_queue_item(session)
    run = ControlledSendService(session, send_settings(global_outreach_kill_switch=True, email_sending_enabled=True, controlled_send_enabled=True, provider_send_enabled=True)).run(campaign.slug, 5, commit=True)
    assert run.status.value == "BLOCKED_BY_GLOBAL_KILL_SWITCH"
    assert item.queue_status == EmailSendQueueStatus.BLOCKED_BY_GLOBAL_KILL_SWITCH
