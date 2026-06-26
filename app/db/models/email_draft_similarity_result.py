from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import DraftSimilarityDecision
from app.db.base import Base, utc_now


class EmailDraftSimilarityResult(Base):
    __tablename__ = "email_draft_similarity_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    compared_against_draft_id: Mapped[int | None] = mapped_column(ForeignKey("email_draft_variants.id"), nullable=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    repeated_phrases_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    decision: Mapped[DraftSimilarityDecision] = mapped_column(Enum(DraftSimilarityDecision, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
