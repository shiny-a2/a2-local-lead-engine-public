from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ManualReviewStatus, Phase4ReviewType
from app.db.base import Base, TimestampMixin


class Phase4ManualReviewItem(TimestampMixin, Base):
    __tablename__ = "phase4_manual_review_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    review_type: Mapped[Phase4ReviewType] = mapped_column(Enum(Phase4ReviewType, native_enum=False))
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    recommended_action: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[ManualReviewStatus] = mapped_column(
        Enum(ManualReviewStatus, native_enum=False), default=ManualReviewStatus.OPEN
    )

