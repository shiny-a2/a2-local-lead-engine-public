from email.message import EmailMessage

from app.core.enums import ProviderStatus
from app.services.null_dry_run_provider import NullDryRunProvider
from app.services.provider_readiness_service import ProviderReadinessService
from app.settings import Settings


def test_null_dry_run_provider_sends_nothing():
    result = NullDryRunProvider().send(EmailMessage(), dry_run=True)
    assert result.provider_status == ProviderStatus.DRY_RUN


def test_provider_readiness_hides_secrets(session):
    _, notes, profile = ProviderReadinessService(session, Settings(smtp_password="secret")).check()
    assert "secret-" not in str(profile.notes_json)
    assert notes
