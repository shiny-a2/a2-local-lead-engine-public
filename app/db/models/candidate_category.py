from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SourceName
from app.db.base import Base, utc_now


class CandidateCategory(Base):
    __tablename__ = "candidate_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    raw_category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    canonical_category: Mapped[str] = mapped_column(String(120), nullable=False)
    canonical_subcategory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    confidence: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    candidate_business = relationship("CandidateBusiness", back_populates="categories")

