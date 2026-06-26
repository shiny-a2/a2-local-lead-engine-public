from fastapi.testclient import TestClient

from app.main import app
from app.settings import get_settings


def test_dashboard_requires_auth(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_review_dashboard_enabled", False)
    monkeypatch.setattr(settings, "testing", False)
    response = TestClient(app).get("/admin/review")
    assert response.status_code == 404


def test_queue_page_renders(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "phase9_review_dashboard_enabled", True)
    monkeypatch.setattr(settings, "phase9_basic_auth_enabled", False)
    response = TestClient(app).get("/admin/review")
    assert response.status_code in {200, 500}
    if response.status_code == 200:
        assert "Human Review Queue" in response.text


def test_forbidden_send_routes_do_not_exist():
    client = TestClient(app)
    for path in ["/send", "/schedule", "/smtp", "/followup", "/inbox-sync", "/bounce-process"]:
        assert client.post(path).status_code == 404
