from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.email_send_queue import EmailSendQueue


class DuplicateSendGuardService:
    def __init__(self, session: Session):
        self.session = session

    def idempotency_key(self, campaign_id: int, candidate_id: int, recipient_email: str) -> str:
        return f"{campaign_id}:{candidate_id}:{recipient_email.lower()}"

    def check(self, key: str) -> tuple[bool, str]:
        row = self.session.scalar(select(EmailSendQueue).where(EmailSendQueue.idempotency_key == key))
        if row and row.queue_status.value in {"SENT_TO_PROVIDER", "READY_TO_SEND_CONTROLLED", "SENDING"}:
            return False, "duplicate_send"
        return True, "ok"
