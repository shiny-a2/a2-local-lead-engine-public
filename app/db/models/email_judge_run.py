from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailJudgeMode, EmailJudgeOperation, EmailJudgeRunStatus
from app.db.base import Base, utc_now


class EmailJudgeRun(Base):
    __tablename__ = "email_judge_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    operation: Mapped[EmailJudgeOperation] = mapped_column(Enum(EmailJudgeOperation, native_enum=False))
    status: Mapped[EmailJudgeRunStatus] = mapped_column(Enum(EmailJudgeRunStatus, native_enum=False))
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    judge_mode: Mapped[EmailJudgeMode] = mapped_column(Enum(EmailJudgeMode, native_enum=False))
    model_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    input_draft_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_with_warnings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rewrite_required_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manual_review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
