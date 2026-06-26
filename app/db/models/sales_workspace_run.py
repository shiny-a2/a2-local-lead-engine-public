from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SalesWorkspaceRunOperation, SalesWorkspaceRunStatus
from app.db.base import Base, utc_now


class SalesWorkspaceRun(Base):
    __tablename__ = "sales_workspace_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    operation: Mapped[SalesWorkspaceRunOperation] = mapped_column(
        Enum(SalesWorkspaceRunOperation, native_enum=False)
    )
    status: Mapped[SalesWorkspaceRunStatus] = mapped_column(
        Enum(SalesWorkspaceRunStatus, native_enum=False)
    )
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    input_opportunity_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    workspace_item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tasks_created_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checklists_created_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
