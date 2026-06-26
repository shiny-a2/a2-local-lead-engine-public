from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def test_dashboard_pages_render_rtl_persian(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase10_send_dashboard_enabled", True)
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    response = TestClient(app).get("/admin/send")
    assert response.status_code == 200
    assert "dir='rtl'" in response.text
    assert "داشبورد ارسال" in response.text


def test_no_send_all_button(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase10_send_dashboard_enabled", True)
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    response = TestClient(app).get("/admin/send/queue")
    assert "send all" not in response.text.lower()
    assert "ارسال همه" not in response.text
