from app.services.secrets_audit_service import SecretsAuditService


def test_secrets_audit_redacts_status(test_settings):
    test_settings.openai_api_key = "sk-test-secret"
    status = SecretsAuditService().secret_status(test_settings)
    assert status["OPENAI_API_KEY"] == "PRESENT"


def test_secrets_audit_detects_raw_secret_text():
    findings = SecretsAuditService().scan_text("OPENAI_API_KEY=sk-secret-value")
    assert findings
