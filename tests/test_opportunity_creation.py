from app.core.enums import OpportunityStatus
from tests.phase12_helpers import build_opportunity_from_body


def test_positive_reply_creates_opportunity(session):
    _, _, _, opp = build_opportunity_from_body(session, "yes interested")
    assert opp.opportunity_status == OpportunityStatus.QUALIFIED_INTEREST


def test_asking_price_creates_price_opportunity(session):
    _, _, _, opp = build_opportunity_from_body(session, "what is the price?")
    assert opp.opportunity_status == OpportunityStatus.ASKED_PRICE


def test_asking_details_creates_details_opportunity(session):
    _, _, _, opp = build_opportunity_from_body(session, "send details please")
    assert opp.opportunity_status == OpportunityStatus.ASKED_DETAILS


def test_requested_call_creates_call_opportunity(session):
    _, _, _, opp = build_opportunity_from_body(session, "give me a call")
    assert opp.opportunity_status == OpportunityStatus.CALL_REQUESTED


def test_not_interested_closes(session):
    _, _, _, opp = build_opportunity_from_body(session, "not interested")
    assert opp.opportunity_status == OpportunityStatus.CLOSED_NOT_INTERESTED


def test_unsubscribe_does_not_create_active_opportunity(session):
    _, _, _, opp = build_opportunity_from_body(session, "unsubscribe")
    assert opp.opportunity_status == OpportunityStatus.CLOSED_UNSUBSCRIBED
