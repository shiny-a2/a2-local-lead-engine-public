from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import DraftPrecheckStatus
from app.db.base import Base, utc_now


class EmailDraftPrecheckResult(Base):
    __tablename__ = "email_draft_precheck_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    precheck_status: Mapped[DraftPrecheckStatus] = mapped_column(Enum(DraftPrecheckStatus, native_enum=False))
    word_count_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    subject_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    personalization_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    blocked_words_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    claim_permission_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    economic_claim_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tone_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cta_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    unsubscribe_placeholder_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    similarity_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    prompt_injection_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    risk_flags_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
