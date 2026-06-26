from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import WebsiteStatus
from app.db.base import Base, TimestampMixin


class LeadWebPresence(TimestampMixin, Base):
    __tablename__ = "lead_web_presence"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    website_status: Mapped[WebsiteStatus] = mapped_column(
        Enum(WebsiteStatus, native_enum=False), default=WebsiteStatus.UNKNOWN, nullable=False
    )
    official_website_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    facebook_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    social_only: Mapped[bool] = mapped_column(default=False, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    lead = relationship("Lead", back_populates="web_presence")

