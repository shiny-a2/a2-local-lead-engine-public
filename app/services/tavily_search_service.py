from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app.core.enums import SearchQueryStatus, SensitiveOperation, SourceName
from app.core.fingerprints import stable_fingerprint
from app.core.safety import check_operation
from app.db.models.search_query import SearchQuery
from app.settings import Settings


class TavilySearchService:
    def __init__(self, settings: Settings, session: Session | None = None):
        self.settings = settings
        self.session = session

    def check_config(self) -> tuple[bool, str]:
        if not self.settings.tavily_api_key:
            return False, "TAVILY_API_KEY_MISSING"
        return True, "CONFIGURED"

    def budget_ok(self, query_count: int) -> bool:
        return (
            query_count <= self.settings.tavily_max_queries_per_run
            and query_count <= self.settings.tavily_daily_query_budget
        )

    def can_execute(self, query_count: int) -> tuple[bool, str]:
        if not check_operation(self.settings, SensitiveOperation.LIVE_API_CALL).allowed:
            return False, "LIVE_API_CALLS_DISABLED"
        if not self.settings.website_verification_enabled:
            return False, "WEBSITE_VERIFICATION_DISABLED"
        ready, reason = self.check_config()
        if not ready:
            return False, reason
        if not self.budget_ok(query_count):
            return False, "TAVILY_BUDGET_EXCEEDED"
        return True, "ALLOWED"

    def execute(self, query_text: str, dry_run: bool) -> dict:
        if dry_run:
            return {"dry_run": True, "results": []}
        allowed, reason = self.can_execute(1)
        if not allowed:
            return {"blocked": True, "reason": reason, "results": []}
        response = httpx.post(
            "https://api.tavily.com/search",
            json={"api_key": self.settings.tavily_api_key, "query": query_text},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def record_query(self, verification_run_id: int, candidate_id: int, planned, dry_run: bool) -> SearchQuery:
        row = SearchQuery(
            verification_run_id=verification_run_id,
            candidate_business_id=candidate_id,
            source_name=SourceName.TAVILY,
            query_text_redacted=planned.query_text,
            query_type=planned.query_type,
            cache_key=planned.cache_key or stable_fingerprint(planned.query_text),
            dry_run=dry_run,
            executed_at=None if dry_run else datetime.now(UTC),
            status=SearchQueryStatus.SKIPPED_DRY_RUN if dry_run else SearchQueryStatus.PLANNED,
        )
        if self.session is not None:
            self.session.add(row)
            self.session.commit()
            self.session.refresh(row)
        return row

