from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def test_persian_rtl_dashboard_renders(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    client = TestClient(app)
    response = client.get("/admin/sales")
    assert response.status_code == 200
    assert 'dir="rtl"' in response.text
    assert "داشبورد فروش دستی" in response.text
    assert "ارسال پاسخ" in response.text
    assert "payment link" in response.text


def test_no_send_reply_meeting_payment_buttons(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    client = TestClient(app)
    response = client.get("/admin/sales/opportunities")
    assert response.status_code == 200
    forbidden = ["Send all", "ارسال quote</button>", "رزرو جلسه</button>", "ساخت payment link</button>"]
    assert all(term not in response.text for term in forbidden)


def test_task_page_renders(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    client = TestClient(app)
    response = client.get("/admin/sales/tasks")
    assert response.status_code == 200
    assert "وظایف فروش" in response.text
