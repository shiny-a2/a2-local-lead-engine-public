from app.core.enums import EmailDraftVariantStatus
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_generation_run import EmailGenerationRun
from app.services.draft_similarity_service import DraftSimilarityService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_similarity_blocks_repeated_drafts(session):
    campaign, candidate = make_phase7_ready_candidate(session)
    run = EmailGenerationRun(run_id="sim-run", campaign_id=campaign.id, operation="phase7_full_generation", status="STARTED")
    session.add(run)
    session.flush()
    body = "same phrase " * 40
    first = EmailDraftVariant(candidate_business_id=candidate.id, email_generation_run_id=run.id, variant_label="A", subject_text="Idea", body_text=body, word_count=80, tone_profile="plain", campaign_lane="NO_WEBSITE", category="barber", status=EmailDraftVariantStatus.DRAFT_CREATED)
    second = EmailDraftVariant(candidate_business_id=candidate.id, email_generation_run_id=run.id, variant_label="B", subject_text="Idea", body_text=body, word_count=80, tone_profile="plain", campaign_lane="NO_WEBSITE", category="barber", status=EmailDraftVariantStatus.DRAFT_CREATED)
    session.add_all([first, second])
    session.flush()
    result = DraftSimilarityService(session, Settings(email_max_similarity_score=0.82)).compare(second)
    assert result.decision.value == "BLOCKED_TOO_SIMILAR"
