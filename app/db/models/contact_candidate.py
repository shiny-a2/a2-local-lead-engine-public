from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ContactRiskLevel, ContactSourceType, ContactType
from app.db.base import Base, utc_now


class ContactCandidate(Base):
    __tablename__ = "contact_candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    contact_type: Mapped[ContactType] = mapped_column(Enum(ContactType, native_enum=False))
    contact_value: Mapped[str] = mapped_column(String(1000), nullable=False)
    contact_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    contact_source_type: Mapped[ContactSourceType] = mapped_column(
        Enum(ContactSourceType, native_enum=False)
    )
    confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    risk_level: Mapped[ContactRiskLevel] = mapped_column(Enum(ContactRiskLevel, native_enum=False))
    allowed_for_outreach: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    blocked_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

