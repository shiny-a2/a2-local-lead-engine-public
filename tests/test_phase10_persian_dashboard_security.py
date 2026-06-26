from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def test_dashboard_requires_auth_when_configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase10_send_dashboard_enabled", True)
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", True)
    monkeypatch.setattr(settings, "phase9_review_username", "amirali")
    response = TestClient(app).get("/admin/send")
    assert response.status_code == 401


def test_no_secrets_visible(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase10_send_dashboard_enabled", True)
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    monkeypatch.setattr(settings, "smtp_password", "secret-password")
    response = TestClient(app).get("/admin/send/provider-readiness")
    assert "secret-password" not in response.text
