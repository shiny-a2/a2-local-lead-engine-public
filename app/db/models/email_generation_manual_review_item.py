from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailGenerationReviewType, ManualReviewStatus
from app.db.base import Base, TimestampMixin


class EmailGenerationManualReviewItem(TimestampMixin, Base):
    __tablename__ = "email_generation_manual_review_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    email_generation_run_id: Mapped[int] = mapped_column(ForeignKey("email_generation_runs.id"))
    email_draft_variant_id: Mapped[int | None] = mapped_column(ForeignKey("email_draft_variants.id"), nullable=True)
    review_type: Mapped[EmailGenerationReviewType] = mapped_column(Enum(EmailGenerationReviewType, native_enum=False))
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[ManualReviewStatus] = mapped_column(Enum(ManualReviewStatus, native_enum=False))
