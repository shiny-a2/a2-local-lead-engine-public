from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class MessageSendSnapshot(Base):
    __tablename__ = "message_send_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_send_queue_id: Mapped[int] = mapped_column(ForeignKey("email_send_queue.id"))
    final_subject_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    final_body_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    unsubscribe_url_snapshot: Mapped[str] = mapped_column(String(1000), nullable=False)
    sender_snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    recipient_snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    subject_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    body_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    unsubscribe_url_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    final_message_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
