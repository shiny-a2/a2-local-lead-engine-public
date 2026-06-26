from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class PromptTemplateSnapshot(Base):
    __tablename__ = "prompt_template_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_generation_run_id: Mapped[int] = mapped_column(ForeignKey("email_generation_runs.id"))
    template_id: Mapped[int] = mapped_column(ForeignKey("email_prompt_templates.id"))
    template_slug: Mapped[str] = mapped_column(String(160), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    system_prompt_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    user_prompt_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    output_schema_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    model_config_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
