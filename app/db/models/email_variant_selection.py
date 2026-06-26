from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class EmailVariantSelection(Base):
    __tablename__ = "email_variant_selections"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_judge_run_id: Mapped[int] = mapped_column(ForeignKey("email_judge_runs.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    preferred_email_draft_variant_id: Mapped[int | None] = mapped_column(ForeignKey("email_draft_variants.id"), nullable=True)
    backup_email_draft_variant_id: Mapped[int | None] = mapped_column(ForeignKey("email_draft_variants.id"), nullable=True)
    selection_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    rejected_variant_ids_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
