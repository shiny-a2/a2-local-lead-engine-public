from app.services.mailbox_readiness_service import MailboxReadinessService
from app.settings import Settings


def test_reply_to_mailbox_readiness_stored(session):
    row = MailboxReadinessService(session, Settings(mailbox_reply_to_email="hello@example.com")).record()
    assert row.reply_to_email == "hello@example.com"


def test_inbox_sync_and_bounce_processing_not_implemented(session):
    row = MailboxReadinessService(session, Settings()).record()
    assert row.inbox_monitoring_mode.value == "planned_only"
    assert row.bounce_processing_mode.value == "planned_only"
    assert "No IMAP" in row.notes_json[0]
