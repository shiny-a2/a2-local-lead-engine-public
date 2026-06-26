from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class EmailRewriteBrief(Base):
    __tablename__ = "email_rewrite_briefs"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_judge_run_id: Mapped[int] = mapped_column(ForeignKey("email_judge_runs.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    rewrite_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    rewrite_instructions_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    must_keep_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    must_remove_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    must_soften_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
