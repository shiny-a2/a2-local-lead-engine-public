from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ContactStatus, EmailType
from app.db.base import Base, TimestampMixin


class CandidateContactVerification(TimestampMixin, Base):
    __tablename__ = "candidate_contact_verifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    best_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    best_email_type: Mapped[EmailType | None] = mapped_column(
        Enum(EmailType, native_enum=False), nullable=True
    )
    best_email_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_contact_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    contact_status: Mapped[ContactStatus] = mapped_column(Enum(ContactStatus, native_enum=False))
    outreach_contact_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    decision_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

