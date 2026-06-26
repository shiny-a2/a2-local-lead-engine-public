from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def test_phase14_dashboard_renders_persian_rtl(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    client = TestClient(app)
    response = client.get("/admin/pilot")
    assert response.status_code == 200
    assert 'dir="rtl"' in response.text
    assert "داشبورد پایلوت" in response.text
    assert "ارسال ایمیل" in response.text


def test_phase14_dashboard_requires_auth_by_default(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", True)
    monkeypatch.setattr(settings, "testing", False)
    monkeypatch.setattr(settings, "phase9_review_username", "")
    client = TestClient(app)
    response = client.get("/admin/pilot")
    assert response.status_code == 401
