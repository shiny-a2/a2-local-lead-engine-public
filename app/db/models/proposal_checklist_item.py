from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ProposalChecklistItemStatus
from app.db.base import Base, TimestampMixin


class ProposalChecklistItem(TimestampMixin, Base):
    __tablename__ = "proposal_checklist_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    proposal_checklist_id: Mapped[int] = mapped_column(ForeignKey("proposal_checklists.id"))
    item_key: Mapped[str] = mapped_column(String(120), nullable=False)
    item_label: Mapped[str] = mapped_column(String(255), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[ProposalChecklistItemStatus] = mapped_column(
        Enum(ProposalChecklistItemStatus, native_enum=False)
    )
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
