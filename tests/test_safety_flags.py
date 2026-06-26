from app.core.enums import SensitiveOperation
from app.core.safety import check_operation


def test_email_sending_blocked_by_default(test_settings):
    result = check_operation(test_settings, SensitiveOperation.EMAIL_SENDING)
    assert result.allowed is False
    assert result.reason == "EMAIL_SENDING_DISABLED"


def test_voice_calls_blocked_by_default(test_settings):
    assert check_operation(test_settings, SensitiveOperation.VOICE_CALL).allowed is False


def test_google_maps_blocked_by_default(test_settings):
    result = check_operation(test_settings, SensitiveOperation.GOOGLE_MAPS_USAGE)
    assert result.allowed is False
    assert result.reason == "GOOGLE_MAPS_PROHIBITED_FOR_MVP"


def test_live_api_calls_blocked_by_default(test_settings):
    assert check_operation(test_settings, SensitiveOperation.LIVE_API_CALL).allowed is False


def test_public_dashboard_blocked_by_default(test_settings):
    assert check_operation(test_settings, SensitiveOperation.PUBLIC_DASHBOARD).allowed is False

