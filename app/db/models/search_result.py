from datetime import datetime

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import DomainClassification, SearchResultType
from app.db.base import Base, utc_now


class SearchResult(Base):
    __tablename__ = "search_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    search_query_id: Mapped[int] = mapped_column(ForeignKey("search_queries.id"))
    candidate_business_id: Mapped[int] = mapped_column(ForeignKey("candidate_businesses.id"))
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    snippet: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    result_type: Mapped[SearchResultType] = mapped_column(Enum(SearchResultType, native_enum=False))
    domain_classification: Mapped[DomainClassification | None] = mapped_column(
        Enum(DomainClassification, native_enum=False), nullable=True
    )
    raw_payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

