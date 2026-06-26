from app.core.enums import EmailProviderType, ProviderStatus, SendAttemptStatus
from app.services.email_provider_base import ProviderResult
from app.services.provider_response_normalizer import ProviderResponseNormalizer


def test_smtp_success_and_failure_normalized():
    svc = ProviderResponseNormalizer()
    assert svc.attempt_status(ProviderResult(EmailProviderType.CPANEL_SMTP, ProviderStatus.ACCEPTED)) == SendAttemptStatus.SENT_TO_PROVIDER
    assert svc.attempt_status(ProviderResult(EmailProviderType.CPANEL_SMTP, ProviderStatus.FAILED, error_type="SMTPError")) == SendAttemptStatus.FAILED_SMTP_ERROR
