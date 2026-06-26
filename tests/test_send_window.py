from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.send_window_service import SendWindowService
from tests.phase10_helpers import send_settings


def test_outside_window_blocks():
    settings = send_settings(send_window_enabled=True, send_window_start="09:00", send_window_end="16:30")
    ok, reason = SendWindowService(settings).check(datetime(2026, 5, 26, 7, 0, tzinfo=ZoneInfo("Pacific/Auckland")))
    assert ok is False
    assert reason == "outside_send_window"


def test_inside_window_passes():
    settings = send_settings(send_window_enabled=True, send_window_start="09:00", send_window_end="16:30")
    ok, _ = SendWindowService(settings).check(datetime(2026, 5, 26, 10, 0, tzinfo=ZoneInfo("Pacific/Auckland")))
    assert ok is True
