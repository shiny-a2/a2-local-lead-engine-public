from app.core.enums import ReplyClassificationValue
from app.services.reply_classification_service import ReplyClassificationService
from app.services.suppression_from_inbound_service import SuppressionFromInboundService
from tests.phase11_helpers import import_message, inbox_settings, sample_email


def test_remove_me_classified_and_suppressed(session):
    _, message = import_message(session, msg=sample_email(body="please remove me"))
    classification = ReplyClassificationService(session, inbox_settings()).classify(message)
    applied = SuppressionFromInboundService(session, inbox_settings()).apply_for_reply(
        message, classification
    )
    assert classification.classification == ReplyClassificationValue.UNSUBSCRIBE_REQUEST
    assert applied is True
