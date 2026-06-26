from sqlalchemy import JSON, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EmailDraftStatus
from app.db.base import Base, TimestampMixin


class EmailDraft(TimestampMixin, Base):
    __tablename__ = "email_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    offer_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    personalization_points_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[EmailDraftStatus] = mapped_column(
        Enum(EmailDraftStatus, native_enum=False), default=EmailDraftStatus.BLOCKED, nullable=False
    )

    judgements = relationship(
        "EmailJudgement", back_populates="draft", cascade="all, delete-orphan"
    )
