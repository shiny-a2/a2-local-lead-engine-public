from app.core.enums import SendAttemptStatus
from app.services.email_provider_base import ProviderResult


class ProviderResponseNormalizer:
    def attempt_status(self, result: ProviderResult) -> SendAttemptStatus:
        if result.provider_status.value == "dry_run":
            return SendAttemptStatus.DRY_RUN_PLANNED
        if result.provider_status.value == "accepted":
            return SendAttemptStatus.SENT_TO_PROVIDER
        if result.error_type and "SMTP" in result.error_type:
            return SendAttemptStatus.FAILED_SMTP_ERROR
        return SendAttemptStatus.FAILED_PROVIDER_ERROR
