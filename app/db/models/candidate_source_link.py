from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CandidateSourceLinkType, SourceName
from app.db.base import Base, utc_now


class CandidateSourceLink(Base):
    __tablename__ = "candidate_source_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    raw_source_record_id: Mapped[int] = mapped_column(ForeignKey("raw_source_records.id"))
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    link_type: Mapped[CandidateSourceLinkType] = mapped_column(
        Enum(CandidateSourceLinkType, native_enum=False)
    )
    match_score: Mapped[float] = mapped_column(Float, default=100, nullable=False)
    match_reasons_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    risk_flags_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    candidate_business = relationship("CandidateBusiness", back_populates="source_links")

