from datetime import datetime

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class EmailDraftEvidenceLink(Base):
    __tablename__ = "email_draft_evidence_links"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    evidence_type: Mapped[str] = mapped_column(String(120), nullable=False)
    evidence_source_table: Mapped[str] = mapped_column(String(120), nullable=False)
    evidence_source_id: Mapped[int | None] = mapped_column(nullable=True)
    used_in_sentence: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
