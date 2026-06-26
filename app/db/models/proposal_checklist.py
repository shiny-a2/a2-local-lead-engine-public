from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ProposalChecklistStatus, ProposalType
from app.db.base import Base, TimestampMixin


class ProposalChecklist(TimestampMixin, Base):
    __tablename__ = "proposal_checklists"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"), unique=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    proposal_type: Mapped[ProposalType] = mapped_column(Enum(ProposalType, native_enum=False))
    status: Mapped[ProposalChecklistStatus] = mapped_column(
        Enum(ProposalChecklistStatus, native_enum=False)
    )
    readiness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
