from app.db.models.email_draft import EmailDraft
from app.db.models.email_send import EmailSend
from app.services.email_writer_service import EmailWriterService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_phase7_creates_no_send_or_approval_records(session):
    campaign, _ = make_phase7_ready_candidate(session)
    EmailWriterService(session, Settings()).generate(campaign.slug, None, 10, commit=True)
    assert session.query(EmailSend).count() == 0
    assert session.query(EmailDraft).count() == 0
