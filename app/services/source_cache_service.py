from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SourceName
from app.core.fingerprints import stable_fingerprint
from app.core.redaction import redact_mapping
from app.db.models.source_cache import SourceCache


class SourceCacheService:
    def __init__(self, session: Session):
        self.session = session

    def make_cache_key(self, source_name: SourceName, params: dict[str, Any]) -> str:
        safe = redact_mapping(params)
        return f"{source_name.value}:{stable_fingerprint(safe)}"

    def get(self, cache_key: str) -> dict[str, Any] | None:
        row = self.session.scalar(select(SourceCache).where(SourceCache.cache_key == cache_key))
        now = datetime.now(UTC).replace(tzinfo=None)
        expires_at = row.expires_at if row is not None else None
        if row is None or expires_at is None or expires_at <= now:
            return None
        return row.response_json

    def set(
        self,
        source_name: SourceName,
        cache_key: str,
        request_params: dict[str, Any],
        response_json: dict[str, Any],
        ttl_days: int,
    ) -> SourceCache:
        row = self.session.scalar(select(SourceCache).where(SourceCache.cache_key == cache_key))
        now = datetime.now(UTC).replace(tzinfo=None)
        if row is None:
            row = SourceCache(
                source_name=source_name,
                cache_key=cache_key,
                request_hash=stable_fingerprint(redact_mapping(request_params)),
                response_json=response_json,
                expires_at=now + timedelta(days=ttl_days),
            )
            self.session.add(row)
        else:
            row.response_json = response_json
            row.expires_at = now + timedelta(days=ttl_days)
            row.updated_at = now
        self.session.commit()
        return row
