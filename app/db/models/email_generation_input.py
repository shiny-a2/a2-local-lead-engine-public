from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class EmailGenerationInput(Base):
    __tablename__ = "email_generation_inputs"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_generation_run_id: Mapped[int] = mapped_column(ForeignKey("email_generation_runs.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    phase6_decision_id: Mapped[int | None] = mapped_column(ForeignKey("phase6_candidate_decisions.id"), nullable=True)
    input_snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    input_snapshot_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    allowed_claims_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    blocked_claims_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    offer_blocks_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    verified_evidence_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    style_constraints_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    cta_options_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
