from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def test_dashboard_pages_render_rtl_persian(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    client = TestClient(app)
    response = client.get("/admin/inbox")
    assert response.status_code == 200
    assert 'dir="rtl"' in response.text
    assert "داشبورد پاسخ‌ها" in response.text
    assert "ارسال follow-up" in response.text
    assert "Send all" not in response.text


def test_mailbox_readiness_page_hides_secrets(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    monkeypatch.setattr(settings, "imap_password", "secret-password")
    client = TestClient(app)
    response = client.get("/admin/inbox/mailbox-readiness")
    assert response.status_code == 200
    assert "secret-password" not in response.text
    assert "redacted" in response.text
