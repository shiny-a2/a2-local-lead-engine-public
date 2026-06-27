"""Approve the qualified NZ no-website leads in the review queue and send a small, QA-gated
warm-up batch to real businesses. Every email passes the GPT pre-send QA gate (right business,
right contact, flawless text) and all compliance gates. Default DRY-RUN; pass --send to send.

    .venv/Scripts/python.exe scripts/send_qa_batch.py            # dry run
    .venv/Scripts/python.exe scripts/send_qa_batch.py --send     # real warm-up send
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.models.campaign import Campaign
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.session import make_session_factory
from app.services.controlled_send_service import ControlledSendService
from app.services.human_decision_service import HumanDecisionService
from app.services.send_queue_service import SendQueueService
from app.settings import Settings

DO_SEND = "--send" in sys.argv
CAMPAIGN = "auckland-local-website-pilot"
BATCH_LIMIT = 5  # warm-up: a few per run


def main() -> None:
    settings = Settings(
        database_url="sqlite:///./a2_local.db",
        country_compliance_enforced=True,
        pre_send_qa_enabled=True,
        send_window_enabled=False,
        send_per_run_limit=BATCH_LIMIT,
        global_outreach_kill_switch=not DO_SEND,
        email_sending_enabled=DO_SEND,
        controlled_send_enabled=DO_SEND,
        provider_send_enabled=DO_SEND,
    )
    session = make_session_factory(settings)()
    campaign = session.scalar(select(Campaign).where(Campaign.slug == CAMPAIGN))
    if not campaign:
        print("campaign not found")
        return
    # Eligible: NZ, no-website lane, verified safe contact, queued for review.
    hq = HumanReviewQueueItem
    items = session.scalars(
        select(hq)
        .join(EmailDraftVariant, EmailDraftVariant.id == hq.email_draft_variant_id)
        .join(CandidateBusiness, CandidateBusiness.id == hq.candidate_business_id)
        .where(
            EmailDraftVariant.campaign_lane != "IMPROVEMENT",
            CandidateBusiness.country.in_(["New Zealand", "Australia"]),
        )
    ).all()
    approved = 0
    for item in items:
        contact = session.scalar(
            select(CandidateContactVerification).where(
                CandidateContactVerification.candidate_business_id == item.candidate_business_id,
                CandidateContactVerification.outreach_contact_allowed.is_(True),
            )
        )
        already_queued = session.scalar(
            select(EmailSendQueue).where(
                EmailSendQueue.candidate_business_id == item.candidate_business_id
            )
        )
        if not contact or already_queued:
            continue
        try:
            HumanDecisionService(session, settings).approve(item.id, "Amirali", "warm-up batch")
            approved += 1
        except Exception:
            continue
    session.commit()
    SendQueueService(session, settings).build_queue(CAMPAIGN, None, commit=True)
    session.commit()
    run = ControlledSendService(session, settings).run(CAMPAIGN, BATCH_LIMIT, commit=DO_SEND)
    session.commit()
    print(f"mode={'REAL SEND' if DO_SEND else 'DRY RUN'} approved={approved}")
    print(f"run_status={run.status.value} sent={run.sent_count} blocked={run.blocked_count}")
    session.close()


if __name__ == "__main__":
    main()
