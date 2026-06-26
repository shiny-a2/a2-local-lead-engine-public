from sqlalchemy import JSON, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CampaignStatus
from app.db.base import Base, TimestampMixin


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    target_city: Mapped[str] = mapped_column(String(120), nullable=False)
    target_country: Mapped[str] = mapped_column(String(120), nullable=False)
    target_categories_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, native_enum=False), default=CampaignStatus.DRAFT, nullable=False
    )
    daily_send_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    manual_approval_required: Mapped[bool] = mapped_column(default=True, nullable=False)

    leads = relationship("Lead", back_populates="campaign")

