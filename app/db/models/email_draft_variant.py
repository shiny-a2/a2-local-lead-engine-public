from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailDraftVariantStatus
from app.db.base import Base, TimestampMixin


class EmailDraftVariant(TimestampMixin, Base):
    __tablename__ = "email_draft_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_draft_id: Mapped[int | None] = mapped_column(ForeignKey("email_drafts.id"), nullable=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    email_generation_run_id: Mapped[int] = mapped_column(ForeignKey("email_generation_runs.id"))
    variant_label: Mapped[str] = mapped_column(String(20), nullable=False)
    subject_text: Mapped[str] = mapped_column(String(255), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    tone_profile: Mapped[str] = mapped_column(String(120), nullable=False)
    campaign_lane: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[EmailDraftVariantStatus] = mapped_column(Enum(EmailDraftVariantStatus, native_enum=False))
