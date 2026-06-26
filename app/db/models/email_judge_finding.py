from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailJudgeFindingType, GateSeverity
from app.db.base import Base, utc_now


class EmailJudgeFinding(Base):
    __tablename__ = "email_judge_findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_judge_run_id: Mapped[int] = mapped_column(ForeignKey("email_judge_runs.id"))
    email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    finding_type: Mapped[EmailJudgeFindingType] = mapped_column(Enum(EmailJudgeFindingType, native_enum=False))
    severity: Mapped[GateSeverity] = mapped_column(Enum(GateSeverity, native_enum=False))
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
