from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailGenerationOperation, EmailGenerationRunStatus
from app.db.base import Base, utc_now


class EmailGenerationRun(Base):
    __tablename__ = "email_generation_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    operation: Mapped[EmailGenerationOperation] = mapped_column(Enum(EmailGenerationOperation, native_enum=False))
    status: Mapped[EmailGenerationRunStatus] = mapped_column(Enum(EmailGenerationRunStatus, native_enum=False))
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    model_provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    prompt_template_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    input_candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    draft_created_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manual_review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
