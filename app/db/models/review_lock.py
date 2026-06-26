from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ReviewLockStatus
from app.db.base import Base, utc_now


class ReviewLock(Base):
    __tablename__ = "review_locks"
    id: Mapped[int] = mapped_column(primary_key=True)
    queue_item_id: Mapped[int] = mapped_column(ForeignKey("human_review_queue_items.id"))
    locked_by: Mapped[str] = mapped_column(String(120), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[ReviewLockStatus] = mapped_column(Enum(ReviewLockStatus, native_enum=False))
