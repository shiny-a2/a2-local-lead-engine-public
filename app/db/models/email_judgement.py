from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import JudgementDecision
from app.db.base import Base, utc_now


class EmailJudgement(Base):
    __tablename__ = "email_judgements"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("email_drafts.id"), nullable=False)
    judge_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision: Mapped[JudgementDecision] = mapped_column(Enum(JudgementDecision, native_enum=False))
    truthfulness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    personalization_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    spam_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    legal_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    flags_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    required_fixes_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    draft = relationship("EmailDraft", back_populates="judgements")

