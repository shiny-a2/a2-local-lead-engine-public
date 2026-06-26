from sqlalchemy import JSON, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SenderIdentityStatus, SenderProviderType
from app.db.base import Base, TimestampMixin


class SenderIdentityProfile(TimestampMixin, Base):
    __tablename__ = "sender_identity_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    provider_type: Mapped[SenderProviderType] = mapped_column(Enum(SenderProviderType, native_enum=False))
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_name: Mapped[str] = mapped_column(String(255), nullable=False)
    reply_to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SenderIdentityStatus] = mapped_column(Enum(SenderIdentityStatus, native_enum=False))
    readiness_notes_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
