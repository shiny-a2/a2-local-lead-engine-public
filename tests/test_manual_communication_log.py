from app.core.enums import ManualCommunicationType
from app.db.models.email_send import EmailSend
from app.services.manual_communication_log_service import ManualCommunicationLogService
from tests.phase12_helpers import build_opportunity_from_body


def test_manual_reply_logged(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    log = ManualCommunicationLogService(session).log(
        opportunity, ManualCommunicationType.MANUAL_REPLY_SENT, "Replied manually", "Amirali"
    )
    assert log.sent_by_human is True


def test_manual_quote_and_proposal_logged_no_actual_send(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    service = ManualCommunicationLogService(session)
    service.log(opportunity, ManualCommunicationType.MANUAL_QUOTE_SENT, "Manual quote outside system", "Amirali")
    service.log(opportunity, ManualCommunicationType.MANUAL_PROPOSAL_SENT, "Manual proposal outside system", "Amirali")
    assert session.query(EmailSend).count() == 0
