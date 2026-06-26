from tests.phase10_helpers import make_phase10_queue_item, send_once


def test_recipient_cooldown_blocks_resend(session):
    _, _, item, _ = make_phase10_queue_item(session)
    send_once(session, item)
    from app.services.send_limit_service import CooldownGuardService
    from tests.phase10_helpers import send_settings

    ok, flags = CooldownGuardService(session, send_settings()).check(item.recipient_email, item.candidate_business_id, item.campaign_id)
    assert ok is False
    assert "recipient_cooldown" in flags
