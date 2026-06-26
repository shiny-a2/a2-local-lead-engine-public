from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import HumanReviewAuditAction
from app.db.base import Base, utc_now


class HumanReviewAuditEvent(Base):
    __tablename__ = "human_review_audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    queue_item_id: Mapped[int] = mapped_column(ForeignKey("human_review_queue_items.id"))
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[HumanReviewAuditAction] = mapped_column(Enum(HumanReviewAuditAction, native_enum=False))
    before_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
