from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SourceName
from app.db.base import Base, utc_now


class NormalizedLocation(Base):
    __tablename__ = "normalized_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    raw_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    normalized_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    suburb: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_hash: Mapped[str | None] = mapped_column(String(80), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    candidate_business = relationship("CandidateBusiness", back_populates="locations")

