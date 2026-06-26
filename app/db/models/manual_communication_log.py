from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ManualCommunicationChannel, ManualCommunicationType
from app.db.base import Base, utc_now


class ManualCommunicationLog(Base):
    __tablename__ = "manual_communication_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunity_records.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    communication_type: Mapped[ManualCommunicationType] = mapped_column(
        Enum(ManualCommunicationType, native_enum=False)
    )
    channel: Mapped[ManualCommunicationChannel] = mapped_column(
        Enum(ManualCommunicationChannel, native_enum=False)
    )
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    sent_by_human: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
