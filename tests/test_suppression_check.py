from app.core.enums import SuppressionReason
from app.db.models.suppression import SuppressionList
from app.services.suppression_check_service import SuppressionCheckService


def test_email_suppression_blocks_approval(session):
    session.add(SuppressionList(email="hello@example.com", reason=SuppressionReason.UNSUBSCRIBED, source="test"))
    session.flush()
    ok, flags = SuppressionCheckService(session).check("hello@example.com")
    assert ok is False
    assert flags


def test_domain_suppression_blocks_approval(session):
    session.add(SuppressionList(domain="example.com", reason=SuppressionReason.MANUAL_BLOCK, source="test"))
    session.flush()
    ok, _ = SuppressionCheckService(session).check("hello@example.com")
    assert ok is False


def test_no_suppression_passes(session):
    assert SuppressionCheckService(session).check("hello@example.com") == (True, [])
