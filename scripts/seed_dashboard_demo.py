"""Seed a few end-to-end leads into a2_local.db so the dashboards show a full funnel.

Creates Phase-7-ready sample candidates, writes GPT drafts, runs the rule judge, builds
the human-review queue, and a pilot governance audit. Nothing is sent.

    .venv/Scripts/python.exe scripts/seed_dashboard_demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import make_session_factory
from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
from app.services.email_writer_service import EmailWriterService
from app.services.human_review_queue_service import HumanReviewQueueService
from app.services.pilot_audit_service import PilotAuditService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate

SAMPLES = [
    ("Ponsonby Hair Co", "Ponsonby", "beauty_salon"),
    ("Mount Eden Barbers", "Mount Eden", "barber"),
    ("Grey Lynn Beauty Lounge", "Grey Lynn", "beauty_salon"),
    ("Kingsland Sharp Cuts", "Kingsland", "barber"),
    ("Devonport Nail Studio", "Devonport", "beauty_salon"),
]


def main() -> None:
    settings = Settings(
        ai_generation_enabled=True,
        email_drafting_enabled=True,
        email_judge_enabled=True,
        email_judge_mode="RULE_ONLY",
    )
    if not settings.openai_api_key:
        print("No OPENAI_API_KEY in .env; aborting.")
        return
    session = make_session_factory(settings)()
    made = 0
    for name, suburb, category in SAMPLES:
        campaign, candidate = make_phase7_ready_candidate(session, category=category)
        candidate.display_name = name
        candidate.canonical_name = name
        candidate.suburb = suburb
        session.commit()
        EmailWriterService(session, settings).generate(campaign.slug, None, 10, commit=True)
        EmailJudgeOrchestratorService(session, settings).judge_emails(
            campaign.slug, None, commit=True
        )
        HumanReviewQueueService(session, settings).build_queue(campaign.slug, None, commit=True)
        PilotAuditService(session, settings).run(campaign.slug, True)
        session.commit()
        made += 1
        print(f"seeded: {name} ({suburb})")
    print(f"done: {made} sample leads now flow through to the review queue + governance.")
    session.close()


if __name__ == "__main__":
    main()
