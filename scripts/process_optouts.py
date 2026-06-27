"""Fetch the info@ mailbox and turn any 'unsubscribe' replies into suppressions, so opt-outs
are honoured automatically. Safe to run on a schedule (daily/hourly). Sends nothing.

    .venv/Scripts/python.exe scripts/process_optouts.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.session import make_session_factory
from app.services.clean_reply_extraction_service import CleanReplyExtractionService
from app.services.lead_response_status_service import LeadResponseStatusService
from app.services.mailbox_sync_service import MailboxSyncService
from app.services.reply_classification_service import ReplyClassificationService
from app.services.suppression_from_inbound_service import SuppressionFromInboundService
from app.services.thread_matching_service import ThreadMatchingService
from app.settings import get_settings


def main() -> None:
    settings = get_settings()
    session = make_session_factory(settings)()
    try:
        run = MailboxSyncService(session, settings).sync("default", commit=True)
        session.commit()
        if run.status.value not in {"COMPLETED", "STARTED"}:
            print(f"inbox sync status={run.status.value} (check IMAP config)")
            return
        messages = session.scalars(
            select(InboundEmailMessage).where(InboundEmailMessage.sync_run_id == run.id)
        ).all()
        suppressed = 0
        for message in messages:
            CleanReplyExtractionService(session).extract(message)
            ThreadMatchingService(session).match(message)
            classification = ReplyClassificationService(session, settings).classify(message)
            suppression = SuppressionFromInboundService(session, settings)
            if suppression.apply_for_reply(message, classification):
                suppressed += 1
            if message.matched_send_queue_id:
                queue = session.get(EmailSendQueue, message.matched_send_queue_id)
                if queue:
                    LeadResponseStatusService(session).update(
                        message, classification, queue.campaign_id
                    )
        session.commit()
        print(f"inbox_sync_run={run.run_id} messages={len(messages)} new_suppressions={suppressed}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
