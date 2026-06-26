from app.services.provider_webhook_ingestion_service import ProviderWebhookIngestionService
from tests.phase11_helpers import inbox_settings


def test_webhook_disabled_blocks_event_processing(session):
    row = ProviderWebhookIngestionService(session, inbox_settings()).ingest(
        "mailgun", {"event_type": "bounced", "recipient_email": "a@example.com"}, True
    )
    assert row is None


def test_valid_event_stored_when_enabled(session):
    row = ProviderWebhookIngestionService(
        session, inbox_settings(provider_webhook_events_enabled=True)
    ).ingest("mailgun", {"event_type": "bounced", "recipient_email": "a@example.com"}, True)
    assert row.signature_valid is True


def test_invalid_signature_rejected_without_auto_reply(session):
    row = ProviderWebhookIngestionService(
        session, inbox_settings(provider_webhook_events_enabled=True)
    ).ingest("mailgun", {"event_type": "bounced", "recipient_email": "a@example.com"}, False)
    assert row.signature_valid is False
    assert row.processed is False
