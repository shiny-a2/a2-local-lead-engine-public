import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import UnsubscribeTokenStatus
from app.db.models.unsubscribe_token import UnsubscribeToken
from app.settings import Settings


class UnsubscribeTokenService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create(self, campaign_id: int, candidate_id: int, recipient_email: str, queue_id: int | None = None) -> tuple[UnsubscribeToken, str]:
        raw = secrets.token_urlsafe(32)
        token_hash = self.hash(raw)
        row = UnsubscribeToken(
            token_hash=token_hash,
            campaign_id=campaign_id,
            candidate_business_id=candidate_id,
            recipient_email=recipient_email,
            email_send_queue_id=queue_id,
            status=UnsubscribeTokenStatus.ACTIVE,
            metadata_json={"raw_token_stored": False},
        )
        self.session.add(row)
        self.session.flush()
        return row, raw

    def hash(self, raw: str) -> str:
        secret = self.settings.unsubscribe_token_secret or "local-phase10-secret"
        return hashlib.sha256(f"{secret}:{raw}".encode()).hexdigest()

    def url(self, raw: str) -> str:
        return f"{self.settings.unsubscribe_public_base_url}?token={raw}"

    def find(self, raw: str) -> UnsubscribeToken | None:
        return self.session.scalar(select(UnsubscribeToken).where(UnsubscribeToken.token_hash == self.hash(raw)))
