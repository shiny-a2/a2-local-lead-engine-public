from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ReplyDraftGenerationMode, ReplyDraftSuggestionStatus
from app.db.base import Base, utc_now


class ReplyDraftSuggestion(Base):
    __tablename__ = "reply_draft_suggestions"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    inbound_message_id: Mapped[int] = mapped_column(ForeignKey("inbound_email_messages.id"))
    draft_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    draft_body: Mapped[str] = mapped_column(Text, nullable=False)
    generation_mode: Mapped[ReplyDraftGenerationMode] = mapped_column(Enum(ReplyDraftGenerationMode, native_enum=False))
    status: Mapped[ReplyDraftSuggestionStatus] = mapped_column(Enum(ReplyDraftSuggestionStatus, native_enum=False))
    risk_flags_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
