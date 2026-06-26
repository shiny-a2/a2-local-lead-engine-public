from app.core.enums import ProviderCircuitStatus
from app.services.provider_circuit_breaker_service import ProviderCircuitBreakerService
from tests.phase10_helpers import FailingProvider, make_phase10_queue_item, send_once, send_settings


def test_transient_error_retry_planned_and_max_retries_enforced(session):
    _, _, item, _ = make_phase10_queue_item(session)
    run = send_once(session, item, provider=FailingProvider(transient=True))
    assert run.failed_count == 1
    assert item.retry_count == 0


def test_provider_auth_error_opens_circuit(session):
    _, _, item, _ = make_phase10_queue_item(session)
    settings = send_settings(global_outreach_kill_switch=False, email_sending_enabled=True, controlled_send_enabled=True, provider_send_enabled=True, provider_max_consecutive_failures=1)
    send_once(session, item, settings=settings, provider=FailingProvider("SMTPAuthenticationError", transient=False))
    circuit = ProviderCircuitBreakerService(session, settings).get(settings.email_provider_slug)
    assert circuit.circuit_status == ProviderCircuitStatus.OPEN
