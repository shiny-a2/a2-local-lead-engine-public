from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import DuplicateClusterStatus
from app.db.base import Base, utc_now


class DuplicateCluster(Base):
    __tablename__ = "duplicate_clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    normalization_run_id: Mapped[int] = mapped_column(ForeignKey("normalization_runs.id"))
    cluster_key: Mapped[str] = mapped_column(String(128), nullable=False)
    cluster_status: Mapped[DuplicateClusterStatus] = mapped_column(
        Enum(DuplicateClusterStatus, native_enum=False)
    )
    candidate_business_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_businesses.id"), nullable=True
    )
    raw_record_ids_json: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    cluster_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    cluster_reasons_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    risk_flags_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

