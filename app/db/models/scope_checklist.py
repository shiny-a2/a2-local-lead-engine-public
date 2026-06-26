from sqlalchemy import Boolean, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ChecklistStatus, ScopeChecklistType
from app.db.base import Base, TimestampMixin


class ScopeChecklist(TimestampMixin, Base):
    __tablename__ = "scope_checklists"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"), unique=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    checklist_type: Mapped[ScopeChecklistType] = mapped_column(
        Enum(ScopeChecklistType, native_enum=False)
    )
    status: Mapped[ChecklistStatus] = mapped_column(Enum(ChecklistStatus, native_enum=False))
    completeness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quote_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    proposal_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
