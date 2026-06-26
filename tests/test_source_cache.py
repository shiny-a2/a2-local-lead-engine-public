from datetime import UTC, datetime, timedelta

from app.core.enums import SourceName
from app.db.models.source_cache import SourceCache
from app.services.source_cache_service import SourceCacheService


def test_cache_key_stable(session):
    service = SourceCacheService(session)
    a = service.make_cache_key(SourceName.GEOAPIFY, {"apiKey": "secret", "q": "x"})
    b = service.make_cache_key(SourceName.GEOAPIFY, {"apiKey": "secret", "q": "x"})
    assert a == b
    assert "secret" not in a


def test_cache_hit_avoids_live_request_path(session):
    service = SourceCacheService(session)
    key = service.make_cache_key(SourceName.GEOAPIFY, {"q": "x"})
    service.set(SourceName.GEOAPIFY, key, {"q": "x"}, {"features": []}, 7)
    assert service.get(key) == {"features": []}


def test_expired_cache_ignored(session):
    key = "geoapify:expired"
    session.add(
        SourceCache(
            source_name=SourceName.GEOAPIFY,
            cache_key=key,
            request_hash="hash",
            response_json={"secret": "not-a-config-secret"},
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
    )
    session.commit()
    assert SourceCacheService(session).get(key) is None


def test_cache_response_does_not_expose_secrets(session):
    service = SourceCacheService(session)
    key = service.make_cache_key(SourceName.GEOAPIFY, {"OPENAI_API_KEY": "sk-secret"})
    assert "sk-secret" not in key

