from app.services.mailbox_sync_service import MailboxSyncService
from tests.phase11_helpers import import_message, inbox_settings, sample_email


def test_dry_run_imports_nothing(session):
    settings = inbox_settings()
    run = MailboxSyncService(session, settings).sync("default", commit=False)
    assert run.dry_run is True
    assert run.messages_imported == 0


def test_duplicate_sync_does_not_import_same_message_twice(session):
    settings = inbox_settings()
    run, message = import_message(session, settings, sample_email(uid="1"))
    duplicate = MailboxSyncService(session, settings).import_message(
        run, sample_email(uid="1"), "1"
    )
    assert message is not None
    assert duplicate is None


def test_plan_reports_no_delete_or_mark_read_by_default(session):
    plan = MailboxSyncService(session, inbox_settings()).plan("default")
    assert "INBOX_SYNC_DISABLED" in plan["gaps"]
    assert plan["imports_messages"] is False
