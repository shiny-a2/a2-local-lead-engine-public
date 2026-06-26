from app.core.enums import BounceType
from app.services.bounce_detection_service import BounceDetectionService
from app.services.suppression_from_inbound_service import SuppressionFromInboundService
from tests.phase11_helpers import import_message, inbox_settings, sample_email


def test_hard_bounce_detected_and_suppressed(session):
    _, message = import_message(
        session,
        msg=sample_email(subject="Delivery Status Notification", body="User unknown"),
    )
    bounce = BounceDetectionService(session).create_event(message)
    assert bounce.bounce_type == BounceType.HARD_BOUNCE
    assert SuppressionFromInboundService(session, inbox_settings()).apply_for_bounce(bounce) is True
    assert bounce.suppression_applied is True


def test_unknown_bounce_requires_review(session):
    _, message = import_message(
        session,
        msg=sample_email(subject="Undeliverable", body="mystery failure"),
    )
    bounce = BounceDetectionService(session).create_event(message)
    assert bounce.manual_review_required is True
