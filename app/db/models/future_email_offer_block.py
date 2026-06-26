from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import FutureEmailBlockType
from app.db.base import Base, utc_now


class FutureEmailOfferBlock(Base):
    __tablename__ = "future_email_offer_blocks"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    block_type: Mapped[FutureEmailBlockType] = mapped_column(Enum(FutureEmailBlockType, native_enum=False))
    block_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    allowed_for_phase7: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_judge: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    risk_flags_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    supporting_evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
