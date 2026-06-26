from app.services.unsubscribe_token_service import UnsubscribeTokenService
from tests.phase10_helpers import send_settings


def test_token_hash_stored_raw_not_stored(session):
    token, raw = UnsubscribeTokenService(session, send_settings()).create(1, 1, "hello@example.com")
    assert raw not in token.token_hash
    assert token.metadata_json["raw_token_stored"] is False


def test_unsubscribe_url_generated():
    assert "token=abc" in UnsubscribeTokenService(None, send_settings()).url("abc")
