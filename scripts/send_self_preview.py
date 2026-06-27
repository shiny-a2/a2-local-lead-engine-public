"""Send ONE real generated lead email to your OWN inbox (info@amiraliyaghouti.com) so you
see exactly what a business would receive - subject, body, and the working reply-unsubscribe.
Nothing is sent to any real business. Run:

    .venv/Scripts/python.exe scripts/send_self_preview.py
"""
import sys
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.models.candidate_business import CandidateBusiness
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.session import make_session_factory
from app.services.cpanel_smtp_provider import CpanelSmtpProvider
from app.services.list_unsubscribe_header_service import ListUnsubscribeHeaderService
from app.settings import get_settings


def main() -> None:
    settings = get_settings()
    to_self = settings.default_from_email or settings.smtp_from_email
    if not to_self or not settings.smtp_password:
        print("SMTP / sender not configured in .env")
        return
    session = make_session_factory(settings)()
    try:
        draft = session.scalar(
            select(EmailDraftVariant)
            .where(EmailDraftVariant.campaign_lane != "IMPROVEMENT")
            .order_by(EmailDraftVariant.id)
        )
        if draft is None:
            print("no draft found - run the pipeline first")
            return
        candidate = session.get(CandidateBusiness, draft.candidate_business_id)
    finally:
        session.close()

    from_email = to_self
    optout = (
        f"To stop receiving these emails, reply with the word UNSUBSCRIBE, or email "
        f"{from_email} with the subject Unsubscribe and you will be removed."
    )
    body = draft.body_text.replace(settings.email_unsubscribe_placeholder, optout)

    msg = EmailMessage()
    msg["From"] = f"{settings.default_from_name} <{from_email}>"
    msg["To"] = to_self
    msg["Reply-To"] = from_email
    msg["Subject"] = f"[PREVIEW lead email] {draft.subject_text}"
    ListUnsubscribeHeaderService().add(
        msg, "", from_email, settings.unsubscribe_one_click_enabled
    )
    msg.set_content(
        f"This is a PREVIEW of the email that would go to: "
        f"{candidate.display_name if candidate else '?'}.\n"
        f"--- begin email ---\n\n{body}\n\n--- end email ---"
    )
    result = CpanelSmtpProvider(settings).send(msg, dry_run=False)
    print(f"preview lead: {candidate.display_name if candidate else '?'}")
    print(f"sent_to_self: {to_self}")
    print(f"provider_status: {result.provider_status.value}")
    print(f"error: {result.error_type or 'none'} {result.error_message or ''}")


if __name__ == "__main__":
    main()
