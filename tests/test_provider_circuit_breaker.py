from app.core.enums import EmailSendQueueStatus
from app.services.provider_circuit_breaker_service import ProviderCircuitBreakerService
from tests.phase10_helpers import make_phase10_queue_item, send_once, send_settings


def test_open_circuit_blocks_send(session):
    _, _, item, _ = make_phase10_queue_item(session)
    settings = send_settings(global_outreach_kill_switch=False, email_sending_enabled=True, controlled_send_enabled=True, provider_send_enabled=True, provider_max_consecutive_failures=1)
    ProviderCircuitBreakerService(session, settings).record_failure(settings.email_provider_slug, "auth")
    run = send_once(session, item, settings=settings)
    assert run.blocked_count == 1
    assert item.queue_status == EmailSendQueueStatus.BLOCKED_BY_PROVIDER_CIRCUIT_BREAKER
