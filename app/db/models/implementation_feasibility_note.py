from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import FeasibilityLevel, MaintenanceRisk
from app.db.base import Base, utc_now


class ImplementationFeasibilityNote(Base):
    __tablename__ = "implementation_feasibility_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    insight_run_id: Mapped[int] = mapped_column(ForeignKey("insight_runs.id"))
    module_slug: Mapped[str] = mapped_column(String(160), nullable=False)
    feasibility_level: Mapped[FeasibilityLevel] = mapped_column(Enum(FeasibilityLevel, native_enum=False))
    implementation_note: Mapped[str] = mapped_column(String(500), nullable=False)
    risk_level: Mapped[MaintenanceRisk] = mapped_column(Enum(MaintenanceRisk, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
