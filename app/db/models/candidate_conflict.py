from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ConflictType
from app.db.base import Base, utc_now


class CandidateConflict(Base):
    __tablename__ = "candidate_conflicts"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_businesses.id"), nullable=True
    )
    duplicate_cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("duplicate_clusters.id"), nullable=True
    )
    conflict_type: Mapped[ConflictType] = mapped_column(Enum(ConflictType, native_enum=False))
    severity: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
