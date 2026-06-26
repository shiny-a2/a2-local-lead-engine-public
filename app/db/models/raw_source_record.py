from datetime import datetime

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RawRecordType, SourceName
from app.db.base import Base, utc_now


class RawSourceRecord(Base):
    __tablename__ = "raw_source_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_run_id: Mapped[int] = mapped_column(ForeignKey("source_runs.id"), nullable=False)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    source_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    record_type: Mapped[RawRecordType] = mapped_column(Enum(RawRecordType, native_enum=False))
    raw_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_suburb: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_phone: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_website: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    raw_opening_hours_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    raw_social_links_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    record_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(default=utc_now)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    source_run = relationship("SourceRun", back_populates="raw_records")
    evidence = relationship("RawPersonalizationEvidence", back_populates="raw_source_record")

