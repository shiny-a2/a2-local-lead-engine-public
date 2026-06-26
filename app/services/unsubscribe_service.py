from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.enums import SuppressionReason, UnsubscribeEventSource, UnsubscribeTokenStatus
from app.db.models.suppression import SuppressionList
from app.db.models.unsubscribe_event import UnsubscribeEvent
from app.services.unsubscribe_token_service import UnsubscribeTokenService
from app.settings import Settings


class UnsubscribeService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def confirm(self, raw_token: str, ip: str | None = None, user_agent: str | None = None) -> tuple[bool, str]:
        token = UnsubscribeTokenService(self.session, self.settings).find(raw_token)
        if token is None:
            return False, "invalid_or_used_token"
        if token.status != UnsubscribeTokenStatus.ACTIVE:
            return False, "invalid_or_used_token"
        token.status = UnsubscribeTokenStatus.USED
        token.used_at = datetime.now(UTC)
        self.session.add(UnsubscribeEvent(unsubscribe_token_id=token.id, recipient_email=token.recipient_email, campaign_id=token.campaign_id, event_source=UnsubscribeEventSource.PUBLIC_UNSUBSCRIBE_PAGE, ip_address=ip, user_agent=user_agent))
        self.session.add(SuppressionList(email=token.recipient_email.lower(), reason=SuppressionReason.UNSUBSCRIBED, source="unsubscribe"))
        self.session.flush()
        return True, "unsubscribed"
