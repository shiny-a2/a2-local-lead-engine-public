from datetime import datetime

from sqlalchemy import JSON, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SourceName
from app.db.base import Base, utc_now


class SourceCache(Base):
    __tablename__ = "source_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    request_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    response_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

