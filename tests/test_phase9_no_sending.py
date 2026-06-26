from app.db.models.email_send import EmailSend
from app.services.human_decision_service import HumanDecisionService
from tests.phase9_helpers import make_phase9_queue_item


def test_no_email_sends_created_no_send_status(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    HumanDecisionService(session, settings).approve(item.id, "Amirali", "Looks good")
    assert session.query(EmailSend).count() == 0
    assert not any("SEND_READY" in row.queue_status.value for row in [item])


def test_no_followup_inbox_bounce_models_created_by_phase9(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    HumanDecisionService(session, settings).hold(item.id, "Amirali", "Later")
    assert item.queue_status.value == "HELD"
