from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ProviderCircuitStatus, SendAuditAction
from app.db.models.provider_circuit_breaker import ProviderCircuitBreaker
from app.db.models.send_audit_event import SendAuditEvent
from app.settings import Settings


class ProviderCircuitBreakerService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def get(self, provider_slug: str) -> ProviderCircuitBreaker:
        row = self.session.scalar(select(ProviderCircuitBreaker).where(ProviderCircuitBreaker.provider_slug == provider_slug))
        if row is None:
            row = ProviderCircuitBreaker(provider_slug=provider_slug, circuit_status=ProviderCircuitStatus.CLOSED)
            self.session.add(row)
            self.session.flush()
        return row

    def can_send(self, provider_slug: str) -> tuple[bool, str]:
        if not self.settings.provider_circuit_breaker_enabled:
            return True, "disabled"
        row = self.get(provider_slug)
        return row.circuit_status != ProviderCircuitStatus.OPEN, row.circuit_status.value

    def record_failure(self, provider_slug: str, reason: str) -> ProviderCircuitBreaker:
        row = self.get(provider_slug)
        row.consecutive_failure_count += 1
        row.last_failure_at = datetime.now(UTC)
        if row.consecutive_failure_count >= self.settings.provider_max_consecutive_failures:
            row.circuit_status = ProviderCircuitStatus.OPEN
            row.opened_at = datetime.now(UTC)
            row.disabled_reason = reason
            self.session.add(SendAuditEvent(email_send_queue_id=None, actor="system", action=SendAuditAction.PROVIDER_CIRCUIT_OPENED, reason=reason))
        self.session.flush()
        return row

    def record_success(self, provider_slug: str) -> None:
        row = self.get(provider_slug)
        row.consecutive_failure_count = 0
        if row.circuit_status == ProviderCircuitStatus.HALF_OPEN:
            row.circuit_status = ProviderCircuitStatus.CLOSED
        self.session.flush()
