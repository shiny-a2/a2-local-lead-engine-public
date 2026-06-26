from app.core.enums import SenderProviderType
from app.services.sender_identity_readiness_service import SenderIdentityReadinessService
from app.settings import Settings


def test_cpanel_smtp_profile_can_be_represented_as_metadata(session):
    settings = Settings(default_from_email="hello@amiraliyaghouti.com", default_reply_to_email="hello@amiraliyaghouti.com")
    ok, _, profile = SenderIdentityReadinessService(session, settings).readiness()
    profile.provider_type = SenderProviderType.CPANEL_SMTP
    assert ok is True
    assert profile.provider_type == SenderProviderType.CPANEL_SMTP


def test_no_smtp_password_stored(session):
    settings = Settings(default_from_email="hello@amiraliyaghouti.com", default_reply_to_email="hello@amiraliyaghouti.com", smtp_password="secret")
    _, _, profile = SenderIdentityReadinessService(session, settings).readiness()
    assert "secret" not in str(profile.readiness_notes_json)
    assert not hasattr(profile, "smtp_password")


def test_missing_sender_identity_warns(session):
    ok, notes, _ = SenderIdentityReadinessService(session, Settings()).readiness()
    assert ok is False
    assert "sender_identity_not_configured" in notes
