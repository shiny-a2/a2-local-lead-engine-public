from sqlalchemy.orm import Session

from app.core.enums import Actor, SensitiveOperation
from app.core.safety import SafetyCheck, check_all_operations, check_operation
from app.services.audit_service import AuditService
from app.settings import Settings


class SafetyService:
    def __init__(self, settings: Settings, session: Session | None = None):
        self.settings = settings
        self.session = session

    def check(self, operation: SensitiveOperation, run_id: str | None = None) -> SafetyCheck:
        result = check_operation(self.settings, operation)
        if not result.allowed and self.session is not None:
            AuditService(self.session, self.settings).record(
                entity_type="safety",
                action="blocked_sensitive_operation",
                actor=Actor.CLI,
                run_id=run_id,
                metadata=result.model_dump(),
            )
        return result

    def check_all(self) -> list[SafetyCheck]:
        return check_all_operations(self.settings)

