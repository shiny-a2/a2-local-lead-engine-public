from app.services.opportunity_service import OpportunityService
from app.services.reply_classification_service import ReplyClassificationService
from app.services.thread_matching_service import ThreadMatchingService
from tests.phase11_helpers import import_matched_message, inbox_settings


def build_opportunity_from_body(session, body: str):
    campaign, _, _, message = import_matched_message(session, body=body)
    ThreadMatchingService(session).match(message)
    classification = ReplyClassificationService(session, inbox_settings()).classify(message)
    opp = OpportunityService(session, inbox_settings()).create_from_reply(
        message, classification, campaign.id
    )
    session.flush()
    return campaign, message, classification, opp
