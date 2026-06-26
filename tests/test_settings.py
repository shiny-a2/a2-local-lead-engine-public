from app.settings import Settings


def test_defaults_load():
    settings = Settings()
    assert settings.app_name == "A2 Local Lead Engine"
    assert settings.require_manual_approval is True


def test_risky_flags_are_false_by_default():
    settings = Settings()
    assert settings.live_api_calls_enabled is False
    assert settings.lead_collection_enabled is False
    assert settings.ai_generation_enabled is False
    assert settings.email_sending_enabled is False
    assert settings.voice_calls_enabled is False
    assert settings.google_maps_enabled is False
    assert settings.public_dashboard_enabled is False


def test_secrets_are_masked():
    settings = Settings(openai_api_key="sk-test-secret", smtp_password="pw")
    safe = settings.safe_dict()
    assert safe["OPENAI_API_KEY"] == "PRESENT"
    assert safe["SMTP_PASSWORD"] == "PRESENT"
    assert "sk-test-secret" not in str(safe)
    assert "pw" not in str(safe)

