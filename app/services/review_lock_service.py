from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import HumanReviewAuditAction, HumanReviewQueueStatus, ReviewLockStatus
from app.db.models.human_review_audit_event import HumanReviewAuditEvent
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.models.review_lock import ReviewLock
from app.settings import Settings


class ReviewLockService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def lock(self, queue_item_id: int, owner: str) -> ReviewLock:
        now = datetime.now(UTC)
        existing = self.session.scalar(
            select(ReviewLock)
            .where(ReviewLock.queue_item_id == queue_item_id, ReviewLock.status == ReviewLockStatus.ACTIVE)
            .order_by(ReviewLock.id.desc())
        )
        if existing and existing.expires_at.tzinfo is None:
            existing.expires_at = existing.expires_at.replace(tzinfo=UTC)
        if existing and existing.expires_at > now and existing.locked_by != owner:
            raise ValueError("queue item is locked")
        if existing and existing.expires_at <= now:
            existing.status = ReviewLockStatus.EXPIRED
        expires = now + timedelta(minutes=self.settings.phase9_review_lock_ttl_minutes)
        row = ReviewLock(queue_item_id=queue_item_id, locked_by=owner, locked_at=now, expires_at=expires, status=ReviewLockStatus.ACTIVE)
        item = self.session.get(HumanReviewQueueItem, queue_item_id)
        if item:
            item.review_lock_owner = owner
            item.locked_at = now
            item.lock_expires_at = expires
            item.queue_status = HumanReviewQueueStatus.IN_REVIEW
        self.session.add(row)
        self.session.add(HumanReviewAuditEvent(queue_item_id=queue_item_id, actor=owner, action=HumanReviewAuditAction.LOCKED))
        self.session.flush()
        return row

    def unlock(self, queue_item_id: int, owner: str) -> None:
        now = datetime.now(UTC)
        row = self.session.scalar(
            select(ReviewLock).where(ReviewLock.queue_item_id == queue_item_id, ReviewLock.status == ReviewLockStatus.ACTIVE)
        )
        if row:
            row.status = ReviewLockStatus.RELEASED
            row.released_at = now
        item = self.session.get(HumanReviewQueueItem, queue_item_id)
        if item:
            item.review_lock_owner = None
            item.locked_at = None
            item.lock_expires_at = None
        self.session.add(HumanReviewAuditEvent(queue_item_id=queue_item_id, actor=owner, action=HumanReviewAuditAction.UNLOCKED))
        self.session.flush()
