from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import LeadStatus
from app.db.base import Base, TimestampMixin


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    suburb: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, native_enum=False), default=LeadStatus.RAW, nullable=False
    )
    source_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    campaign = relationship("Campaign", back_populates="leads")
    sources = relationship("LeadSource", back_populates="lead", cascade="all, delete-orphan")
    contacts = relationship("LeadContact", back_populates="lead", cascade="all, delete-orphan")
    web_presence = relationship(
        "LeadWebPresence", back_populates="lead", cascade="all, delete-orphan"
    )
    scores = relationship("LeadScore", back_populates="lead", cascade="all, delete-orphan")
