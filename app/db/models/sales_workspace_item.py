from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SalesWorkspaceStatus
from app.db.base import Base, TimestampMixin


class SalesWorkspaceItem(TimestampMixin, Base):
    __tablename__ = "sales_workspace_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"), unique=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    workspace_status: Mapped[SalesWorkspaceStatus] = mapped_column(
        Enum(SalesWorkspaceStatus, native_enum=False)
    )
    priority: Mapped[str] = mapped_column(String(40), nullable=False)
    owner: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(nullable=True)
