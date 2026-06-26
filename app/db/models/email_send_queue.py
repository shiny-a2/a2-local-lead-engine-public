from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailSendQueueStatus
from app.db.base import Base, TimestampMixin


class EmailSendQueue(TimestampMixin, Base):
    __tablename__ = "email_send_queue"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_send_queue_idempotency"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    send_queue_run_id: Mapped[int] = mapped_column(ForeignKey("send_queue_runs.id"))
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    phase9_decision_id: Mapped[int] = mapped_column(ForeignKey("phase9_candidate_decisions.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    email_manual_edit_version_id: Mapped[int | None] = mapped_column(ForeignKey("email_manual_edit_versions.id"), nullable=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_profile_id: Mapped[int] = mapped_column(ForeignKey("sender_provider_configs.id"))
    unsubscribe_token_id: Mapped[int | None] = mapped_column(ForeignKey("unsubscribe_tokens.id"), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    queue_status: Mapped[EmailSendQueueStatus] = mapped_column(Enum(EmailSendQueueStatus, native_enum=False))
    priority_tier: Mapped[str | None] = mapped_column(String(80), nullable=True)
    scheduled_for: Mapped[datetime | None] = mapped_column(nullable=True)
    claimed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    claim_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    next_retry_at: Mapped[datetime | None] = mapped_column(nullable=True)
    permanent_failure: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hold_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
