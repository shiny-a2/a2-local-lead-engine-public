from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CandidateStatus, VerificationReadiness
from app.db.base import Base, TimestampMixin


class CandidateBusiness(TimestampMixin, Base):
    __tablename__ = "candidate_businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    candidate_identity_fingerprint: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False
    )
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_category: Mapped[str] = mapped_column(String(120), nullable=False)
    canonical_subcategory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    suburb: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    address_line: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_hash: Mapped[str | None] = mapped_column(String(80), nullable=True)
    geo_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    identity_confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    category_confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    data_quality_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    duplicate_risk_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    chain_risk_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    generic_name_risk_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    verification_readiness_status: Mapped[VerificationReadiness] = mapped_column(
        Enum(VerificationReadiness, native_enum=False),
        default=VerificationReadiness.NOT_READY_LOW_QUALITY,
        nullable=False,
    )
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus, native_enum=False),
        default=CandidateStatus.CANDIDATE_CREATED,
        nullable=False,
    )
    created_from_run_id: Mapped[str | None] = mapped_column(String(80), nullable=True)

    source_links = relationship("CandidateSourceLink", back_populates="candidate_business")
    aliases = relationship("CandidateAlias", back_populates="candidate_business")
    locations = relationship("NormalizedLocation", back_populates="candidate_business")
    categories = relationship("CandidateCategory", back_populates="candidate_business")
    quality_reports = relationship("CandidateQualityReport", back_populates="candidate_business")
    evidence = relationship(
        "CandidatePersonalizationEvidence", back_populates="candidate_business"
    )

