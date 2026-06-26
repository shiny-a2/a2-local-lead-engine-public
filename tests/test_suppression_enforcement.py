from app.core.enums import SuppressionReason
from app.db.models.suppression import SuppressionList
from app.services.suppression_enforcement_service import SuppressionEnforcementService
from tests.phase10_helpers import make_phase10_queue_item


def test_email_and_domain_suppression_block(session):
    _, _, item, _ = make_phase10_queue_item(session)
    session.add(SuppressionList(domain=item.recipient_domain, reason=SuppressionReason.MANUAL_BLOCK, source="test"))
    session.flush()
    ok, flags = SuppressionEnforcementService(session).check_queue_item(item)
    assert ok is False
    assert flags
