"""The continuous engine re-runs the pipeline every cycle. With pipeline_skip_processed=True a
re-run must NOT re-draft (no duplicate GPT calls / no duplicate drafts for the same business)."""
from app.db.models.email_draft_variant import EmailDraftVariant
from app.services.email_writer_service import EmailWriterService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_email_generate_idempotent_when_skip_processed(session):
    campaign, _ = make_phase7_ready_candidate(session)
    settings = Settings(
        pipeline_skip_processed=True,
        email_drafting_enabled=True,
        email_local_writer_enabled=True,
    )
    EmailWriterService(session, settings).generate(campaign.slug, None, 10, commit=True)
    first = session.query(EmailDraftVariant).count()
    assert first >= 1
    # Second cycle on the same (already-drafted) candidate adds nothing.
    EmailWriterService(session, settings).generate(campaign.slug, None, 10, commit=True)
    assert session.query(EmailDraftVariant).count() == first


def test_email_generate_redrafts_when_flag_off(session):
    # Default behaviour is unchanged: without the flag a re-run still drafts again.
    campaign, _ = make_phase7_ready_candidate(session)
    settings = Settings(email_drafting_enabled=True, email_local_writer_enabled=True)
    EmailWriterService(session, settings).generate(campaign.slug, None, 10, commit=True)
    first = session.query(EmailDraftVariant).count()
    EmailWriterService(session, settings).generate(campaign.slug, None, 10, commit=True)
    assert session.query(EmailDraftVariant).count() > first
