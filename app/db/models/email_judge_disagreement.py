from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import JudgeDisagreementResolution
from app.db.base import Base, utc_now


class EmailJudgeDisagreement(Base):
    __tablename__ = "email_judge_disagreements"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_judge_run_id: Mapped[int] = mapped_column(ForeignKey("email_judge_runs.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    rule_decision: Mapped[str] = mapped_column(String(80), nullable=False)
    ai_decision: Mapped[str | None] = mapped_column(String(80), nullable=True)
    final_resolution: Mapped[JudgeDisagreementResolution] = mapped_column(Enum(JudgeDisagreementResolution, native_enum=False))
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
