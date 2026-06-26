from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ChecklistItemStatus
from app.db.base import Base, TimestampMixin


class ScopeChecklistItem(TimestampMixin, Base):
    __tablename__ = "scope_checklist_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    scope_checklist_id: Mapped[int] = mapped_column(ForeignKey("scope_checklists.id"))
    item_key: Mapped[str] = mapped_column(String(120), nullable=False)
    question_text: Mapped[str] = mapped_column(String(500), nullable=False)
    answer_text: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[ChecklistItemStatus] = mapped_column(
        Enum(ChecklistItemStatus, native_enum=False)
    )
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
