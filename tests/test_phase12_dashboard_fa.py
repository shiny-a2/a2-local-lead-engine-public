from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def test_phase12_dashboard_renders_persian_rtl(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    client = TestClient(app)
    response = client.get("/admin/opportunities")
    assert response.status_code == 200
    assert 'dir="rtl"' in response.text
    assert "داشبورد فرصت‌ها" in response.text
    assert "ارسال پاسخ" in response.text
    assert "payment link" in response.text
    assert "Send" not in response.text


def test_phase12_task_page(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    client = TestClient(app)
    response = client.get("/admin/opportunities/tasks")
    assert response.status_code == 200
    assert "وظایف انسانی" in response.text
