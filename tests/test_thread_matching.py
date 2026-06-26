from app.core.enums import InboundMatchMethod
from app.services.thread_matching_service import ThreadMatchingService
from tests.phase11_helpers import import_matched_message, import_message


def test_x_a2_header_matches_send(session):
    _, queue_item, _, message = import_matched_message(session)
    match = ThreadMatchingService(session).match(message)
    assert match.email_send_queue_id == queue_item.id
    assert match.match_method == InboundMatchMethod.X_A2_HEADERS


def test_subject_only_match_requires_manual_review(session):
    _, message = import_message(session)
    match = ThreadMatchingService(session).match(message)
    assert match.match_method == InboundMatchMethod.SUBJECT_SIMILARITY
    assert match.manual_review_required is True
