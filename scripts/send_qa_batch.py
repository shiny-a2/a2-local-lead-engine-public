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

from app.core.enums import EmailSendQueueStatus
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
BATCH_LIMIT = 8  # warm-up: a few per run; daily cap below bounds total volume


def main() -> None:
    settings = Settings(
        database_url="sqlite:///./a2_local.db",
        country_compliance_enforced=True,
        pre_send_qa_enabled=True,
        send_window_enabled=False,
        send_per_run_limit=BATCH_LIMIT,
        send_daily_limit=30,  # warm-up ceiling; raise as the domain warms
        send_per_domain_daily_limit=1,
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
    # Eligible review items: NZ/AU, non-improvement lane. Dedupe to ONE (latest) per candidate so
    # one business with many review items can't crowd out the rest.
    hq = HumanReviewQueueItem
    items = session.scalars(
        select(hq)
        .join(EmailDraftVariant, EmailDraftVariant.id == hq.email_draft_variant_id)
        .join(CandidateBusiness, CandidateBusiness.id == hq.candidate_business_id)
        .where(
            EmailDraftVariant.campaign_lane != "IMPROVEMENT",
            CandidateBusiness.country.in_(["New Zealand", "Australia"]),
        )
        .order_by(hq.id)
    ).all()
    by_candidate = {item.candidate_business_id: item for item in items}  # highest id wins
    # Skip a candidate ONLY if it already has a queue row that is in flight or settled — NOT
    # SEND_DRY_RUN_PLANNED / transient blocks (those get recovered in build_queue).
    settled_states = {
        EmailSendQueueStatus.QUEUED_FOR_SEND,
        EmailSendQueueStatus.READY_TO_SEND_CONTROLLED,
        EmailSendQueueStatus.SENDING,
        EmailSendQueueStatus.SENT_TO_PROVIDER,
        EmailSendQueueStatus.HELD_BY_OPERATOR,
        EmailSendQueueStatus.CANCELLED_BY_OPERATOR,
    }
    approved = 0
    for cid, item in by_candidate.items():
        contact = session.scalar(
            select(CandidateContactVerification).where(
                CandidateContactVerification.candidate_business_id == cid,
                CandidateContactVerification.outreach_contact_allowed.is_(True),
            )
        )
        if not contact:
            continue
        settled = session.scalar(
            select(EmailSendQueue).where(
                EmailSendQueue.candidate_business_id == cid,
                EmailSendQueue.queue_status.in_(settled_states),
            )
        )
        if settled:
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
