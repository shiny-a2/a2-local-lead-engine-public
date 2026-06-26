from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Phase4WebsiteStatus
from app.db.base import Base, TimestampMixin, utc_now


class CandidateWebPresenceVerification(TimestampMixin, Base):
    __tablename__ = "candidate_web_presence_verifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    website_status: Mapped[Phase4WebsiteStatus] = mapped_column(
        Enum(Phase4WebsiteStatus, native_enum=False)
    )
    official_website_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    official_website_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website_confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    website_ownership_confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    website_strength_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    social_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    directory_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weak_website: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    no_website_claim_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    no_website_claim_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    decision_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(default=utc_now)
    stale_after: Mapped[datetime | None] = mapped_column(nullable=True)
