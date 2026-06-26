from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ManualEditSeverity
from app.db.base import Base, utc_now


class EmailManualEditVersion(Base):
    __tablename__ = "email_manual_edit_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    queue_item_id: Mapped[int] = mapped_column(ForeignKey("human_review_queue_items.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    original_email_draft_variant_id: Mapped[int] = mapped_column(ForeignKey("email_draft_variants.id"))
    previous_version_id: Mapped[int | None] = mapped_column(ForeignKey("email_manual_edit_versions.id"), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subject_text: Mapped[str] = mapped_column(String(255), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    editor: Mapped[str] = mapped_column(String(120), nullable=False)
    edit_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    diff_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    edit_severity: Mapped[ManualEditSeverity] = mapped_column(Enum(ManualEditSeverity, native_enum=False))
    requires_rejudge: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
