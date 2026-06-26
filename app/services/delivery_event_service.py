from sqlalchemy.orm import Session

from app.core.enums import DeliveryEventType, EmailProviderType
from app.db.models.delivery_event import DeliveryEvent


class DeliveryEventService:
    def __init__(self, session: Session):
        self.session = session

    def record_unknown_cpanel(self, queue_id: int, recipient: str) -> DeliveryEvent:
        row = DeliveryEvent(email_send_queue_id=queue_id, provider_type=EmailProviderType.CPANEL_SMTP, event_type=DeliveryEventType.UNKNOWN, recipient_email=recipient, raw_payload_json={"note": "cPanel SMTP acceptance does not prove inbox delivery."})
        self.session.add(row)
        self.session.flush()
        return row
