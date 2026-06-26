from app.services.send_limit_service import SendLimitService
from tests.phase10_helpers import send_settings


def test_per_run_daily_domain_limits_enforced(session):
    settings = send_settings(send_daily_limit=1, send_per_run_limit=1, send_per_domain_daily_limit=1)
    svc = SendLimitService(session, settings)
    assert svc.check(1, "example.com")[0] is True
    svc.increment(1, "example.com")
    ok, flags = svc.check(1, "example.com")
    assert ok is False
    assert flags
