from app.core.enums import Actor
from app.services.audit_service import AuditService


def test_can_write_audit_event(session, test_settings):
    log = AuditService(session, test_settings).record(
        entity_type="test",
        action="created",
        actor=Actor.TEST,
        run_id="run-123",
        metadata={"OPENAI_API_KEY": "sk-secret", "safe": "ok"},
    )
    assert log is not None
    assert log.run_id == "run-123"
    assert log.metadata_json["OPENAI_API_KEY"] == "PRESENT"
    assert "sk-secret" not in str(log.metadata_json)

