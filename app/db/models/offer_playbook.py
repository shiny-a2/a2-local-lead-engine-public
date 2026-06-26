from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import OfferPlaybookStatus
from app.db.base import Base, TimestampMixin


class OfferPlaybook(TimestampMixin, Base):
    __tablename__ = "offer_playbooks"
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    playbook_slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    playbook_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[OfferPlaybookStatus] = mapped_column(Enum(OfferPlaybookStatus, native_enum=False))
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    default_offer_package: Mapped[str] = mapped_column(String(80), nullable=False)
