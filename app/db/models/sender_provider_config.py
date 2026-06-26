from sqlalchemy import JSON, Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailProviderType, SenderProviderConfigStatus, SendWarmupStage
from app.db.base import Base, TimestampMixin


class SenderProviderConfig(TimestampMixin, Base):
    __tablename__ = "sender_provider_configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    provider_type: Mapped[EmailProviderType] = mapped_column(Enum(EmailProviderType, native_enum=False))
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_name: Mapped[str] = mapped_column(String(255), nullable=False)
    reply_to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SenderProviderConfigStatus] = mapped_column(Enum(SenderProviderConfigStatus, native_enum=False))
    daily_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    per_run_limit: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    per_domain_daily_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    warmup_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    warmup_stage: Mapped[SendWarmupStage] = mapped_column(Enum(SendWarmupStage, native_enum=False))
    spf_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    dkim_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    dmarc_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reply_to_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    bounce_handling_mode: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
