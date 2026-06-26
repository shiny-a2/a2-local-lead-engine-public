from app.core.enums import HumanResponseTaskType
from app.services.human_task_service import HumanTaskService
from app.services.reply_classification_service import ReplyClassificationService
from app.services.thread_matching_service import ThreadMatchingService
from tests.phase11_helpers import import_matched_message, inbox_settings


def test_positive_reply_creates_review_task(session):
    _, _, _, message = import_matched_message(session, body="yes interested")
    ThreadMatchingService(session).match(message)
    classification = ReplyClassificationService(session, inbox_settings()).classify(message)
    task = HumanTaskService(session, inbox_settings()).create_for_classification(
        message, classification
    )
    assert task.task_type == HumanResponseTaskType.REVIEW_POSITIVE_REPLY


def test_price_request_creates_price_task(session):
    _, _, _, message = import_matched_message(session, body="how much does it cost?")
    ThreadMatchingService(session).match(message)
    classification = ReplyClassificationService(session, inbox_settings()).classify(message)
    task = HumanTaskService(session, inbox_settings()).create_for_classification(
        message, classification
    )
    assert task.task_type == HumanResponseTaskType.SEND_PRICE_INFO
