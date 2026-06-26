import imaplib
from datetime import UTC, datetime
from email.message import Message

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    InboundAuditAction,
    InboundMessageType,
    InboxSyncOperation,
    InboxSyncStatus,
    Phase11MailboxStatus,
)
from app.core.run_context import RunContext
from app.db.models.inbound_attachment import InboundAttachment
from app.db.models.inbound_audit_event import InboundAuditEvent
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.inbox_sync_run import InboxSyncRun
from app.db.models.mailbox_readiness_profile import MailboxReadinessProfile
from app.services.inbound_message_parser_service import (
    InboundMessageParserService,
    ParsedInboundMessage,
)
from app.settings import Settings


class MailboxSyncService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings
        self.parser = InboundMessageParserService(settings)

    def readiness(self, mailbox: str = "default") -> tuple[MailboxReadinessProfile, list[str]]:
        profile = self.session.scalar(
            select(MailboxReadinessProfile).where(
                MailboxReadinessProfile.profile_slug == mailbox
            )
        )
        if profile is None:
            profile = MailboxReadinessProfile(
                profile_slug=mailbox,
                provider_type="imap",
                mailbox_email=self.settings.imap_username or self.settings.mailbox_reply_to_email,
                imap_host=self.settings.imap_host or None,
                imap_port=self.settings.imap_port,
                use_ssl=self.settings.imap_use_ssl,
                status=Phase11MailboxStatus.DRAFT,
                notes_json={"password_stored_in_db": False},
            )
            self.session.add(profile)
            self.session.flush()
        gaps = []
        if not self.settings.inbox_sync_enabled:
            gaps.append("INBOX_SYNC_DISABLED")
        if not self.settings.imap_sync_enabled:
            gaps.append("IMAP_SYNC_DISABLED")
        if not self.settings.imap_host:
            gaps.append("IMAP_HOST_MISSING")
        if not self.settings.imap_username:
            gaps.append("IMAP_USERNAME_MISSING")
        if not self.settings.imap_password:
            gaps.append("IMAP_PASSWORD_MISSING")
        profile.status = Phase11MailboxStatus.READY if not gaps else Phase11MailboxStatus.DRAFT
        profile.notes_json = {
            "password_stored_in_db": False,
            "mark_read": self.settings.imap_mark_read,
            "delete_messages": self.settings.imap_delete_messages,
            "move_processed": self.settings.imap_move_processed,
        }
        return profile, gaps

    def plan(self, mailbox: str = "default") -> dict:
        profile, gaps = self.readiness(mailbox)
        return {
            "mailbox": mailbox,
            "ready": not gaps,
            "gaps": gaps,
            "last_seen_uid": profile.last_seen_uid,
            "max_messages": self.settings.inbox_sync_max_messages_per_run,
            "imports_messages": False,
            "secrets": "redacted",
        }

    def sync(self, mailbox: str = "default", commit: bool = False) -> InboxSyncRun:
        profile, gaps = self.readiness(mailbox)
        status = InboxSyncStatus.STARTED
        if not commit:
            status = InboxSyncStatus.DRY_RUN_ONLY
        elif gaps:
            status = InboxSyncStatus.BLOCKED_BY_CONFIG
        run = InboxSyncRun(
            run_id=RunContext().run_id,
            provider_type="imap",
            mailbox=self.settings.imap_mailbox,
            operation=InboxSyncOperation.IMAP_SYNC,
            status=status,
            dry_run=not commit,
            metadata_json={
                "gaps": gaps,
                "delete_messages": False,
                "mark_read": self.settings.imap_mark_read,
                "outbound_sent": False,
            },
        )
        self.session.add(run)
        self.session.flush()
        if not commit or gaps:
            run.finished_at = datetime.now(UTC)
            return run
        raw_messages = self._fetch_raw_messages(profile)
        run.messages_seen = len(raw_messages)
        for uid, raw in raw_messages:
            parsed = self.parser.parse_bytes(raw, uid)
            if self.import_parsed(run, parsed) is not None:
                run.messages_imported += 1
                profile.last_seen_uid = uid
        profile.last_sync_at = datetime.now(UTC)
        run.status = InboxSyncStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        return run

    def import_message(self, run: InboxSyncRun, message: Message, uid: str | None = None) -> InboundEmailMessage | None:
        return self.import_parsed(run, self.parser.parse_message(message, uid))

    def import_parsed(
        self, run: InboxSyncRun, parsed: ParsedInboundMessage
    ) -> InboundEmailMessage | None:
        duplicate_key = self.parser.duplicate_key(parsed)
        existing = self.session.scalar(
            select(InboundEmailMessage).where(InboundEmailMessage.duplicate_key == duplicate_key)
        )
        if existing:
            self.session.add(
                InboundAuditEvent(
                    actor="system",
                    action=InboundAuditAction.MESSAGE_SKIPPED_DUPLICATE,
                    reason="duplicate inbound message",
                )
            )
            return None
        row = InboundEmailMessage(
            sync_run_id=run.id,
            provider_type=run.provider_type,
            mailbox=run.mailbox,
            message_uid=parsed.message_uid,
            message_id_header=parsed.message_id_header,
            in_reply_to_header=parsed.in_reply_to_header,
            references_header=parsed.references_header,
            from_email=parsed.from_email,
            from_name=parsed.from_name,
            to_email=parsed.to_email,
            subject=parsed.subject,
            received_at=parsed.received_at,
            raw_headers_json=parsed.raw_headers_json,
            body_text_sanitized=parsed.body_text_sanitized,
            body_hash=parsed.body_hash,
            message_type=InboundMessageType.UNKNOWN,
            duplicate_key=duplicate_key,
        )
        self.session.add(row)
        self.session.flush()
        for attachment in parsed.attachments:
            self.session.add(InboundAttachment(inbound_message_id=row.id, **attachment))
        self.session.add(
            InboundAuditEvent(
                inbound_message_id=row.id,
                actor="system",
                action=InboundAuditAction.MESSAGE_IMPORTED,
                reason="inbound message imported; no outbound action",
            )
        )
        return row

    def _fetch_raw_messages(self, profile: MailboxReadinessProfile) -> list[tuple[str, bytes]]:
        mailbox_cls = imaplib.IMAP4_SSL if self.settings.imap_use_ssl else imaplib.IMAP4
        client = mailbox_cls(self.settings.imap_host, self.settings.imap_port)
        try:
            client.login(self.settings.imap_username, self.settings.imap_password)
            client.select(self.settings.imap_mailbox, readonly=not self.settings.imap_mark_read)
            search_status, data = client.uid("search", "", "ALL")
            if search_status != "OK" or not data:
                return []
            uids = data[0].split()[-self.settings.inbox_sync_max_messages_per_run :]
            results: list[tuple[str, bytes]] = []
            for uid_bytes in uids:
                uid = uid_bytes.decode()
                fetch_status, fetched = client.uid("fetch", uid, "(RFC822)")
                if fetch_status != "OK":
                    continue
                for part in fetched:
                    if isinstance(part, tuple):
                        results.append((uid, part[1]))
                        break
            return results
        finally:
            try:
                client.logout()
            except Exception:
                pass
