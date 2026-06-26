from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import InboundMessageType
from app.db.base import Base, utc_now


class InboundEmailMessage(Base):
    __tablename__ = "inbound_email_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    sync_run_id: Mapped[int] = mapped_column(ForeignKey("inbox_sync_runs.id"))
    provider_type: Mapped[str] = mapped_column(String(80), nullable=False)
    mailbox: Mapped[str] = mapped_column(String(255), nullable=False)
    message_uid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message_id_header: Mapped[str | None] = mapped_column(String(500), nullable=True)
    in_reply_to_header: Mapped[str | None] = mapped_column(String(500), nullable=True)
    references_header: Mapped[str | None] = mapped_column(Text, nullable=True)
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    to_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    received_at: Mapped[datetime] = mapped_column(nullable=False)
    raw_headers_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    body_text_sanitized: Mapped[str] = mapped_column(Text, nullable=False)
    body_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_header_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message_type: Mapped[InboundMessageType] = mapped_column(Enum(InboundMessageType, native_enum=False))
    matched_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    matched_candidate_business_id: Mapped[int | None] = mapped_column(ForeignKey("candidate_businesses.id"), nullable=True)
    duplicate_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
