from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ContactStatus, Phase4Decision, Phase4WebsiteStatus
from app.db.base import Base, utc_now


class Phase4CandidateDecision(Base):
    __tablename__ = "phase4_candidate_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    decision: Mapped[Phase4Decision] = mapped_column(Enum(Phase4Decision, native_enum=False))
    decision_confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    website_status: Mapped[Phase4WebsiteStatus] = mapped_column(
        Enum(Phase4WebsiteStatus, native_enum=False)
    )
    contact_status: Mapped[ContactStatus] = mapped_column(Enum(ContactStatus, native_enum=False))
    ready_for_phase5: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reject_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    warnings_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

