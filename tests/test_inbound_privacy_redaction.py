from app.services.inbound_privacy_redaction_service import InboundPrivacyRedactionService
from tests.phase11_helpers import inbox_settings


def test_secrets_redacted():
    text = InboundPrivacyRedactionService(inbox_settings()).sanitize_text(
        "password: supersecret"
    )
    assert "supersecret" not in text
    assert "redacted" in text


def test_sensitive_headers_limited():
    headers = InboundPrivacyRedactionService(inbox_settings()).safe_headers(
        {"Authorization": "Bearer x", "Subject": "Hi", "Message-ID": "1"}
    )
    assert "Authorization" not in headers
    assert "Subject" in headers
