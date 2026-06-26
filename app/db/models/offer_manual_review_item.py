from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ManualReviewStatus, OfferReviewType
from app.db.base import Base, TimestampMixin


class OfferManualReviewItem(TimestampMixin, Base):
    __tablename__ = "offer_manual_review_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    review_type: Mapped[OfferReviewType] = mapped_column(Enum(OfferReviewType, native_enum=False))
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[ManualReviewStatus] = mapped_column(Enum(ManualReviewStatus, native_enum=False))
