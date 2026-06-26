from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SearchQueryStatus, SearchQueryType, SourceName
from app.db.base import Base, utc_now


class SearchQuery(Base):
    __tablename__ = "search_queries"
    id: Mapped[int] = mapped_column(primary_key=True)
    verification_run_id: Mapped[int] = mapped_column(ForeignKey("verification_runs.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    source_name: Mapped[SourceName] = mapped_column(Enum(SourceName, native_enum=False))
    query_text_redacted: Mapped[str] = mapped_column(String(1000), nullable=False)
    query_type: Mapped[SearchQueryType] = mapped_column(Enum(SearchQueryType, native_enum=False))
    cache_key: Mapped[str] = mapped_column(String(255), nullable=False)
    dry_run: Mapped[bool] = mapped_column(default=True, nullable=False)
    executed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[SearchQueryStatus] = mapped_column(Enum(SearchQueryStatus, native_enum=False))
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

