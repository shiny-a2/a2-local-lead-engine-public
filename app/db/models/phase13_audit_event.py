from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import Phase13AuditAction
from app.db.base import Base, utc_now


class Phase13AuditEvent(Base):
    __tablename__ = "phase13_audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int | None] = mapped_column(
        ForeignKey("opportunity_records.id"), nullable=True
    )
    candidate_business_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_businesses.id"), nullable=True
    )
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[Phase13AuditAction] = mapped_column(Enum(Phase13AuditAction, native_enum=False))
    before_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
