from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailClaimRiskLevel
from app.db.base import Base, utc_now


class EmailDraftClaimUsage(Base):
    __tablename__ = "email_draft_claim_usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    claim_type: Mapped[str] = mapped_column(String(120), nullable=False)
    claim_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    claim_permission_id: Mapped[int | None] = mapped_column(nullable=True)
    allowed: Mapped[bool] = mapped_column(default=False, nullable=False)
    risk_level: Mapped[EmailClaimRiskLevel] = mapped_column(Enum(EmailClaimRiskLevel, native_enum=False))
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
