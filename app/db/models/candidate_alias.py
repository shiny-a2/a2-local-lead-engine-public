from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SourceName
from app.db.base import Base, utc_now


class CandidateAlias(Base):
    __tablename__ = "candidate_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    confidence: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    candidate_business = relationship("CandidateBusiness", back_populates="aliases")

