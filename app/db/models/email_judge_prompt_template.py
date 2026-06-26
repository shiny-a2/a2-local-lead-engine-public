from sqlalchemy import JSON, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailPromptTemplateStatus
from app.db.base import Base, TimestampMixin


class EmailJudgePromptTemplate(TimestampMixin, Base):
    __tablename__ = "email_judge_prompt_templates"
    id: Mapped[int] = mapped_column(primary_key=True)
    template_slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    template_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[EmailPromptTemplateStatus] = mapped_column(Enum(EmailPromptTemplateStatus, native_enum=False))
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    output_schema_json: Mapped[dict] = mapped_column(JSON, nullable=False)
