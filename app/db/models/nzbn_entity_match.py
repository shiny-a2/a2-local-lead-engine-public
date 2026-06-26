from datetime import datetime

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class NzbnEntityMatch(Base):
    __tablename__ = "nzbn_entity_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_source_record_id: Mapped[int] = mapped_column(ForeignKey("raw_source_records.id"))
    source_run_id: Mapped[int] = mapped_column(ForeignKey("source_runs.id"))
    query_name: Mapped[str] = mapped_column(String(255), nullable=False)
    nzbn: Mapped[str | None] = mapped_column(String(80), nullable=True)
    entity_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity_status: Mapped[str | None] = mapped_column(String(120), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    match_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

