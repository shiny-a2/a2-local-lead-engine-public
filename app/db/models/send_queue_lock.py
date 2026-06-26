from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SendQueueLockStatus
from app.db.base import Base, utc_now


class SendQueueLock(Base):
    __tablename__ = "send_queue_locks"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_send_queue_id: Mapped[int] = mapped_column(ForeignKey("email_send_queue.id"))
    lock_owner: Mapped[str] = mapped_column(String(120), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[SendQueueLockStatus] = mapped_column(Enum(SendQueueLockStatus, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
