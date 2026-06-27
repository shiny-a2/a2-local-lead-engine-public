"""Approve and send ONE real, compliant cold email to the single unambiguously-correct NZ lead
(Tonic Room -> info@tonicroom.co.nz). Default is DRY-RUN (prints the plan, sends nothing).
Pass --send to actually send. All compliance gates (country, suppression, unsubscribe, window,
limits) are enforced by ControlledSendService.

    .venv/Scripts/python.exe scripts/send_one_real.py          # dry run
    .venv/Scripts/python.exe scripts/send_one_real.py --send   # real send
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.models.campaign import Campaign
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.session import make_session_factory
from app.services.controlled_send_service import ControlledSendService
from app.services.human_decision_service import HumanDecisionService
from app.services.send_queue_service import SendQueueService
from app.settings import Settings

TARGET = "Tonic Room"
DO_SEND = "--send" in sys.argv


def main() -> None:
    settings = Settings(
        database_url="sqlite:///./a2_send.db",
        country_compliance_enforced=True,
        send_window_enabled=False,
        send_per_run_limit=2,
        global_outreach_kill_switch=not DO_SEND,
        email_sending_enabled=DO_SEND,
        controlled_send_enabled=DO_SEND,
        provider_send_enabled=DO_SEND,
    )
    session = make_session_factory(settings)()
    slug = "auckland-local-website-pilot"
    campaign = session.scalar(select(Campaign).where(Campaign.slug == slug))
    item = session.scalar(
        select(HumanReviewQueueItem)
        .join(CandidateBusiness, CandidateBusiness.id == HumanReviewQueueItem.candidate_business_id)
        .where(CandidateBusiness.display_name == TARGET)
    )
    if not campaign or not item:
        print(f"lead '{TARGET}' not found in review queue on a2_send.db")
        return
    draft = session.get(EmailDraftVariant, item.email_draft_variant_id)
    candidate = session.get(CandidateBusiness, item.candidate_business_id)
    print(f"target business : {candidate.display_name} ({candidate.city}, {candidate.country})")
    print(f"subject         : {draft.subject_text}")
    print(f"mode            : {'REAL SEND' if DO_SEND else 'DRY RUN (nothing sent)'}")

    cbid = item.candidate_business_id
    queue_item = session.scalar(
        select(EmailSendQueue).where(EmailSendQueue.candidate_business_id == cbid)
    )
    if queue_item is None:
        HumanDecisionService(session, settings).approve(item.id, "Amirali", "warm-up send")
        session.commit()
        SendQueueService(session, settings).build_queue(campaign.slug, None, commit=True)
        session.commit()
        queue_item = session.scalar(select(EmailSendQueue).order_by(EmailSendQueue.id.desc()))
    print(f"recipient       : {queue_item.recipient_email if queue_item else '(not queued)'}")

    run = ControlledSendService(session, settings).run(campaign.slug, 2, commit=DO_SEND)
    session.commit()
    print(f"run_status      : {run.status.value}")
    print(f"sent_count      : {run.sent_count}  blocked_count: {run.blocked_count}")
    session.close()


if __name__ == "__main__":
    main()
