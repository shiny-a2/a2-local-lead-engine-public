from app.core.enums import ProviderStatus
from app.services.controlled_send_service import ControlledSendService
from app.services.email_provider_base import ProviderResult
from app.services.human_decision_service import HumanDecisionService
from app.services.send_queue_service import SendQueueService
from app.settings import Settings
from tests.phase9_helpers import make_phase9_queue_item


def send_settings(**overrides):
    data = {
        "default_from_email": "hello@amiraliyaghouti.com",
        "default_reply_to_email": "hello@amiraliyaghouti.com",
        "smtp_host": "mail.example.com",
        "smtp_username": "hello@amiraliyaghouti.com",
        "smtp_password": "secret",
        "send_window_enabled": False,
    }
    data.update(overrides)
    return Settings(**data)


def make_phase10_queue_item(session, settings=None):
    settings = settings or send_settings()
    campaign, _, review_run, item, phase9_settings = make_phase9_queue_item(session)
    HumanDecisionService(session, phase9_settings).approve(item.id, "Amirali", "Looks good")
    session.commit()
    run = SendQueueService(session, settings).build_queue(campaign.slug, review_run.run_id, commit=True)
    from app.db.models.email_send_queue import EmailSendQueue

    queue_item = session.query(EmailSendQueue).first()
    return campaign, run, queue_item, settings


class AcceptedProvider:
    def send(self, message, dry_run: bool):
        from app.core.enums import EmailProviderType

        return ProviderResult(
            provider_type=EmailProviderType.CPANEL_SMTP,
            provider_status=ProviderStatus.ACCEPTED,
            provider_message_id="mock-message-id",
            smtp_response_code="250",
        )


class FailingProvider:
    def __init__(self, error_type="SMTPAuthenticationError", transient=True):
        self.error_type = error_type
        self.transient = transient

    def send(self, message, dry_run: bool):
        from app.core.enums import EmailProviderType

        return ProviderResult(
            provider_type=EmailProviderType.CPANEL_SMTP,
            provider_status=ProviderStatus.FAILED,
            error_type=self.error_type,
            error_message="mock failure",
            transient_error=self.transient,
            permanent_error=not self.transient,
        )


def send_once(session, queue_item, settings=None, provider=None):
    settings = settings or send_settings(
        global_outreach_kill_switch=False,
        email_sending_enabled=True,
        controlled_send_enabled=True,
        provider_send_enabled=True,
    )
    from app.db.models.campaign import Campaign

    campaign_slug = session.get(Campaign, queue_item.campaign_id).slug
    return ControlledSendService(session, settings, provider or AcceptedProvider()).run(
        campaign_slug, 5, commit=True
    )
