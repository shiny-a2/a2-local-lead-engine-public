from datetime import datetime

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class ClaimPermission(Base):
    __tablename__ = "claim_permissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    claim_type: Mapped[str] = mapped_column(String(120), nullable=False)
    allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    approved_phrasing: Mapped[str | None] = mapped_column(String(500), nullable=True)
    blocked_phrasing_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
