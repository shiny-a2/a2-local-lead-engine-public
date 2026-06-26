from datetime import datetime

from sqlalchemy import JSON, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class EmailRuleJudgeResult(Base):
    __tablename__ = "email_rule_judge_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_judge_run_id: Mapped[int] = mapped_column(ForeignKey("email_judge_runs.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    blocker_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    truthfulness_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evidence_alignment_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    blocked_claims_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    unsubscribe_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sender_identity_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cta_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    creepy_evidence_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    economic_claims_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    findings_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
