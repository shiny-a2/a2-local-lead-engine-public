import json

from app.core.enums import EmailGenerationRunStatus
from app.db.models.email_draft_variant import EmailDraftVariant
from app.services.email_writer_service import EmailWriterService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_dry_run_does_not_call_openai(session):
    campaign, _ = make_phase7_ready_candidate(session)
    run = EmailWriterService(session, Settings()).generate(campaign.slug, None, 10, commit=False)
    assert run.status == EmailGenerationRunStatus.DRY_RUN_ONLY
    assert run.metadata_json["openai_calls_attempted"] is False


def test_disabled_ai_blocks_generation(session):
    campaign, _ = make_phase7_ready_candidate(session)
    run = EmailWriterService(session, Settings()).generate(campaign.slug, None, 10, commit=True)
    assert run.status == EmailGenerationRunStatus.BLOCKED_BY_AI_CONFIG


def test_mocked_valid_json_creates_draft_variants(session):
    campaign, _ = make_phase7_ready_candidate(session)
    body = (
        "I was looking at Example Phase Six Studio around Ponsonby and noticed a simple owned page could help customers act directly. "
        "A lightweight services and booking idea could keep the useful details in one place. "
        "It can start small and only grow if useful. "
        "I am Amirali Yaghouti, and I build simple local-business web systems. "
        "Would a quick idea be useful? {{unsubscribe_url}}"
    )
    def client(_):
        return json.dumps({"drafts": [{"variant_label": "A", "subject": "A simple website idea", "body": body, "evidence_keys": ["business_name", "local_context"], "claim_texts": ["owned page"]}]})
    settings = Settings(ai_generation_enabled=True, email_drafting_enabled=True, openai_api_key="sk-test")
    run = EmailWriterService(session, settings, client).generate(campaign.slug, None, 10, commit=True)
    assert run.draft_created_count == 1
    assert session.query(EmailDraftVariant).count() == 1


def test_invalid_json_fails_safely(session):
    campaign, _ = make_phase7_ready_candidate(session)
    settings = Settings(ai_generation_enabled=True, email_drafting_enabled=True, openai_api_key="sk-test")
    run = EmailWriterService(session, settings, lambda _: "not json").generate(campaign.slug, None, 10, commit=True)
    assert run.failed_count == 1
