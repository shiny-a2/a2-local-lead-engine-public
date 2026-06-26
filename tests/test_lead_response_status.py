from app.core.enums import LeadResponseLatestStatus
from app.services.lead_response_status_service import LeadResponseStatusService
from app.services.reply_classification_service import ReplyClassificationService
from app.services.thread_matching_service import ThreadMatchingService
from tests.phase11_helpers import import_matched_message, inbox_settings


def test_positive_reply_updates_status(session):
    campaign, _, _, message = import_matched_message(session, body="yes interested")
    ThreadMatchingService(session).match(message)
    classification = ReplyClassificationService(session, inbox_settings()).classify(message)
    status = LeadResponseStatusService(session).update(message, classification, campaign.id)
    assert status.latest_status == LeadResponseLatestStatus.REPLIED_POSITIVE
    assert status.human_action_required is True


def test_unsubscribe_updates_status(session):
    campaign, _, _, message = import_matched_message(session, body="unsubscribe")
    ThreadMatchingService(session).match(message)
    classification = ReplyClassificationService(session, inbox_settings()).classify(message)
    status = LeadResponseStatusService(session).update(message, classification, campaign.id)
    assert status.latest_status == LeadResponseLatestStatus.UNSUBSCRIBED
    assert status.closed is True
