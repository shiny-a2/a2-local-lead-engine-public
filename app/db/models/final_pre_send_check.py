from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import FinalPreSendCheckStatus
from app.db.base import Base, utc_now


class FinalPreSendCheck(Base):
    __tablename__ = "final_pre_send_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    queue_item_id: Mapped[int] = mapped_column(ForeignKey("human_review_queue_items.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    email_manual_edit_version_id: Mapped[int | None] = mapped_column(ForeignKey("email_manual_edit_versions.id"), nullable=True)
    email_draft_variant_id: Mapped[int | None] = mapped_column(ForeignKey("email_draft_variants.id"), nullable=True)
    check_status: Mapped[FinalPreSendCheckStatus] = mapped_column(Enum(FinalPreSendCheckStatus, native_enum=False))
    sender_identity_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    unsubscribe_placeholder_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recipient_contact_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    suppression_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    claim_safety_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    body_length_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    subject_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    single_cta_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    judge_validity_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    staleness_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    manual_approval_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    mailbox_readiness_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    risk_flags_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
