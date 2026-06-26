from app.core.enums import ReplyClassificationValue
from app.services.reply_classification_service import ReplyClassificationService
from tests.phase11_helpers import import_message, inbox_settings, sample_email


def test_out_of_office_detected_not_positive(session):
    _, message = import_message(session, msg=sample_email(body="Out of office until Tuesday"))
    classification = ReplyClassificationService(session, inbox_settings()).classify(message)
    assert classification.classification == ReplyClassificationValue.OUT_OF_OFFICE
