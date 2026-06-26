from app.core.redaction import redact_database_url, redact_mapping, redact_text


def test_redaction_masks_secret_names():
    safe = redact_mapping({"OPENAI_API_KEY": "sk-raw", "SMTP_PASSWORD": "secret"})
    assert safe["OPENAI_API_KEY"] == "PRESENT"
    assert safe["SMTP_PASSWORD"] == "PRESENT"
    assert "sk-raw" not in str(safe)
    assert "secret" not in str(safe)


def test_database_password_is_masked():
    redacted = redact_database_url("postgresql+psycopg://user:password@localhost:5432/a2")
    assert "password" not in redacted
    assert "***" in redacted


def test_query_text_secret_is_masked():
    redacted = redact_text("OPENAI_API_KEY=sk-raw&TOKEN=abc")
    assert "sk-raw" not in redacted
    assert "abc" not in redacted

