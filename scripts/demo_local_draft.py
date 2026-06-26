"""Demonstrate the FREE keyless drafting chain end to end (Phase 6 -> 7 -> 8 -> 9).

No OpenAI key, no SMTP, nothing sent. Uses the real services: the local template
email writer, the rule-only judge, and the human review queue builder. Run with:

    .venv/Scripts/python.exe scripts/demo_local_draft.py
"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.session import make_session_factory
from app.services.email_judge_orchestrator_service import EmailJudgeOrchestratorService
from app.services.email_writer_service import EmailWriterService
from app.services.human_review_queue_service import HumanReviewQueueService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def main() -> None:
    settings = Settings(
        database_url="sqlite:///./a2_demo.db",
        email_drafting_enabled=True,
        email_local_writer_enabled=True,
        email_judge_enabled=True,
        email_judge_mode="RULE_ONLY",
    )
    # fresh demo db
    from app.db.base import Base
    from app.db.session import make_engine

    engine = make_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = make_session_factory(settings)()
    campaign, candidate = make_phase7_ready_candidate(session, category="beauty_salon")

    writer = EmailWriterService(session, settings)
    gen = writer.generate(campaign.slug, None, 10, commit=True)
    judge = EmailJudgeOrchestratorService(session, settings).judge_emails(
        campaign.slug, None, commit=True
    )
    review = HumanReviewQueueService(session, settings).build_queue(
        campaign.slug, None, commit=True
    )

    draft = session.scalar(select(EmailDraftVariant).order_by(EmailDraftVariant.id))
    decision = session.scalar(select(EmailJudgeDecision).order_by(EmailJudgeDecision.id))
    queue_n = len(session.scalars(select(HumanReviewQueueItem)).all())

    meta = gen.metadata_json or {}
    dec = decision.decision.value if decision else None
    quality = decision.quality_score if decision else None
    print("== FREE keyless drafting chain (no OpenAI / no SMTP) ==")
    print(f"writer_mode        : {meta.get('writer_mode')} "
          f"(openai_attempted={meta.get('openai_calls_attempted')})")
    print(f"drafts_created     : {gen.draft_created_count}")
    print(f"judge_mode         : {judge.judge_mode.value}")
    print(f"judge_decision     : {dec}  quality={quality}")
    print(f"human_queue_items  : {queue_n}  (run_status={review.status.value})")
    print()
    if draft:
        print(f"business : {candidate.display_name} ({candidate.suburb}, {candidate.city})")
        print(f"subject  : {draft.subject_text}")
        print("body     :")
        print(textwrap.indent(textwrap.fill(draft.body_text, 86), "  "))
    session.close()


if __name__ == "__main__":
    main()
