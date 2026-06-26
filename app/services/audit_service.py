from sqlalchemy.orm import Session

from app.core.enums import Actor
from app.core.redaction import redact_mapping
from app.db.models.audit_log import AuditLog
from app.settings import Settings


class AuditService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def record(
        self,
        *,
        entity_type: str,
        action: str,
        actor: Actor = Actor.CLI,
        entity_id: str | None = None,
        run_id: str | None = None,
        before: dict | None = None,
        after: dict | None = None,
        metadata: dict | None = None,
    ) -> AuditLog | None:
        if not self.settings.audit_log_enabled:
            return None
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=actor,
            run_id=run_id,
            before_json=redact_mapping(before or {}) if before is not None else None,
            after_json=redact_mapping(after or {}) if after is not None else None,
            metadata_json=redact_mapping(metadata or {}) if metadata is not None else None,
        )
        self.session.add(log)
        self.session.commit()
        return log

