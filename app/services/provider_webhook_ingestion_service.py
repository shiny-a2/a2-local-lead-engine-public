from sqlalchemy.orm import Session

from app.db.models.provider_webhook_event import ProviderWebhookEvent
from app.settings import Settings


class ProviderWebhookIngestionService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def ingest(self, provider_type: str, payload: dict, signature_valid: bool) -> ProviderWebhookEvent | None:
        if not self.settings.provider_webhook_events_enabled:
            return None
        if not signature_valid:
            return ProviderWebhookEvent(
                provider_type=provider_type,
                event_type=str(payload.get("event_type", "rejected")),
                provider_message_id=payload.get("provider_message_id"),
                recipient_email=str(payload.get("recipient_email", "")),
                signature_valid=False,
                raw_payload_json={"rejected": True},
                processed=False,
            )
        row = ProviderWebhookEvent(
            provider_type=provider_type,
            event_type=str(payload.get("event_type", "unknown")),
            provider_message_id=payload.get("provider_message_id"),
            recipient_email=str(payload.get("recipient_email", "")),
            signature_valid=True,
            raw_payload_json=payload,
            processed=False,
        )
        self.session.add(row)
        self.session.flush()
        return row
