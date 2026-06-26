from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ManualReviewStatus, ManualReviewType
from app.db.base import Base, TimestampMixin


class CandidateManualReviewItem(TimestampMixin, Base):
    __tablename__ = "candidate_manual_review_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_businesses.id"), nullable=True
    )
    duplicate_cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("duplicate_clusters.id"), nullable=True
    )
    review_type: Mapped[ManualReviewType] = mapped_column(Enum(ManualReviewType, native_enum=False))
    severity: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[ManualReviewStatus] = mapped_column(
        Enum(ManualReviewStatus, native_enum=False),
        default=ManualReviewStatus.OPEN,
        nullable=False,
    )

