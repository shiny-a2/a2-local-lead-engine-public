from datetime import UTC, datetime
from email.message import EmailMessage

from app.core.enums import InboxSyncOperation, InboxSyncStatus
from app.db.models.inbox_sync_run import InboxSyncRun
from app.services.mailbox_sync_service import MailboxSyncService
from app.settings import Settings
from tests.phase10_helpers import make_phase10_queue_item


def inbox_settings(**overrides):
    data = {
        "inbound_max_body_chars": 20000,
        "inbox_sync_enabled": False,
        "imap_sync_enabled": False,
        "reply_classification_enabled": True,
    }
    data.update(overrides)
    return Settings(**data)


def sample_email(
    subject="Re: Website idea",
    body="Yes, interested.\n\nOn Monday you wrote:\nold thread",
    from_email="hello@example.com",
    to_email="hello@amiraliyaghouti.com",
    uid="101",
    headers=None,
):
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Message-ID"] = f"<{uid}@example.com>"
    for key, value in (headers or {}).items():
        msg[key] = value
    msg.set_content(body)
    return msg


def make_sync_run(session):
    run = InboxSyncRun(
        run_id="phase11-test-run",
        provider_type="imap",
        mailbox="INBOX",
        operation=InboxSyncOperation.IMAP_SYNC,
        status=InboxSyncStatus.COMPLETED,
        dry_run=False,
        started_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    session.add(run)
    session.flush()
    return run


def import_message(session, settings=None, msg=None):
    settings = settings or inbox_settings()
    run = make_sync_run(session)
    message = MailboxSyncService(session, settings).import_message(
        run, msg or sample_email(), "101"
    )
    session.flush()
    return run, message


def import_matched_message(session, settings=None, body="Yes, interested."):
    campaign, _, queue_item, _ = make_phase10_queue_item(session)
    msg = sample_email(
        body=body,
        headers={"X-A2-Send-Queue-ID": str(queue_item.id)},
        from_email=queue_item.recipient_email,
    )
    run, message = import_message(session, settings or inbox_settings(), msg)
    return campaign, queue_item, run, message
