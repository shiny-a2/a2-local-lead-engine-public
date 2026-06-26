import hashlib

from sqlalchemy.orm import Session

from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_manual_edit_version import EmailManualEditVersion
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.message_send_snapshot import MessageSendSnapshot
from app.db.models.sender_provider_config import SenderProviderConfig
from app.settings import Settings


class MessageSnapshotService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create(
        self,
        item: EmailSendQueue,
        provider: SenderProviderConfig,
        unsubscribe_url: str,
    ) -> MessageSendSnapshot:
        draft = self.session.get(EmailDraftVariant, item.email_draft_variant_id)
        if draft is None:
            raise ValueError("missing approved draft variant")
        version = (
            self.session.get(EmailManualEditVersion, item.email_manual_edit_version_id)
            if item.email_manual_edit_version_id
            else None
        )
        subject = version.subject_text if version else draft.subject_text
        body = version.body_text if version else draft.body_text
        if self.settings.email_unsubscribe_placeholder not in body:
            raise ValueError("missing unsubscribe placeholder")
        final_body = body.replace(self.settings.email_unsubscribe_placeholder, unsubscribe_url)
        if "<html" in final_body.lower():
            raise ValueError("html email blocked")
        row = MessageSendSnapshot(
            email_send_queue_id=item.id,
            final_subject_snapshot=subject,
            final_body_snapshot=final_body,
            unsubscribe_url_snapshot=unsubscribe_url,
            sender_snapshot_json={
                "from_email": provider.from_email,
                "from_name": provider.from_name,
                "reply_to": provider.reply_to_email,
            },
            recipient_snapshot_json={"recipient_email": item.recipient_email},
            subject_hash=self._hash(subject),
            body_hash=self._hash(final_body),
            unsubscribe_url_hash=self._hash(unsubscribe_url),
            final_message_hash=self._hash(subject + "\n" + final_body),
        )
        self.session.add(row)
        self.session.flush()
        return row

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()
