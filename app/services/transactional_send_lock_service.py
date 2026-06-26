from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import EmailSendQueueStatus, SendQueueLockStatus
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.send_queue_lock import SendQueueLock


class TransactionalSendLockService:
    def __init__(self, session: Session):
        self.session = session

    def claim(self, item: EmailSendQueue, owner: str = "cli-send") -> bool:
        if item.queue_status != EmailSendQueueStatus.READY_TO_SEND_CONTROLLED:
            return False
        now = datetime.now(UTC)
        existing = self.session.scalar(select(SendQueueLock).where(SendQueueLock.email_send_queue_id == item.id, SendQueueLock.status == SendQueueLockStatus.ACTIVE))
        if existing and existing.expires_at.tzinfo is None:
            existing.expires_at = existing.expires_at.replace(tzinfo=UTC)
        if existing and existing.expires_at > now:
            return False
        if existing:
            existing.status = SendQueueLockStatus.EXPIRED
        lock = SendQueueLock(email_send_queue_id=item.id, lock_owner=owner, locked_at=now, expires_at=now + timedelta(minutes=10), status=SendQueueLockStatus.ACTIVE)
        item.queue_status = EmailSendQueueStatus.SENDING
        item.claimed_by = owner
        item.claimed_at = now
        item.claim_expires_at = lock.expires_at
        self.session.add(lock)
        self.session.flush()
        return True

    def release(self, item: EmailSendQueue) -> None:
        row = self.session.scalar(select(SendQueueLock).where(SendQueueLock.email_send_queue_id == item.id, SendQueueLock.status == SendQueueLockStatus.ACTIVE))
        if row:
            row.status = SendQueueLockStatus.RELEASED
            row.released_at = datetime.now(UTC)
        item.claimed_by = None
        self.session.flush()
