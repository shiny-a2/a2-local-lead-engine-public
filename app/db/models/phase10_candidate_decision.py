from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Phase10Decision
from app.db.base import Base, utc_now


class Phase10CandidateDecision(Base):
    __tablename__ = "phase10_candidate_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    send_queue_run_id: Mapped[int] = mapped_column(ForeignKey("send_queue_runs.id"))
    email_send_queue_id: Mapped[int | None] = mapped_column(ForeignKey("email_send_queue.id"), nullable=True)
    decision: Mapped[Phase10Decision] = mapped_column(Enum(Phase10Decision, native_enum=False))
    sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    warnings_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
