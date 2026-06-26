from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import GateSeverity, Phase13GateName
from app.db.base import Base, utc_now


class ProposalReadinessGate(Base):
    __tablename__ = "proposal_readiness_gates"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    gate_name: Mapped[Phase13GateName] = mapped_column(Enum(Phase13GateName, native_enum=False))
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    severity: Mapped[GateSeverity] = mapped_column(Enum(GateSeverity, native_enum=False))
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
