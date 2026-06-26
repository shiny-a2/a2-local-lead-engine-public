from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EmailType
from app.db.base import Base, utc_now


class LeadContact(Base):
    __tablename__ = "lead_contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_type: Mapped[EmailType] = mapped_column(
        Enum(EmailType, native_enum=False), default=EmailType.UNKNOWN, nullable=False
    )
    email_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    website_contact_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_allowed_for_outreach: Mapped[bool] = mapped_column(default=False, nullable=False)
    blocked_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    lead = relationship("Lead", back_populates="contacts")

