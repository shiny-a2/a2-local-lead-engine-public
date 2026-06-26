from app.core.enums import Phase4WebsiteStatus, PriorityTier
from app.db.models.pilot_batch_candidate import PilotBatchCandidate
from app.services.lead_scoring_service import LeadScoringService
from app.services.pilot_batch_selection_service import PilotBatchSelectionService
from tests.phase5_helpers import make_phase5_candidate


def test_selects_p1_before_p2_and_respects_limit(session):
    campaign, _ = make_phase5_candidate(session, website_status=Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED, name="P1 Barber")
    make_phase5_candidate(session, campaign, website_status=Phase4WebsiteStatus.DIRECTORY_ONLY, name="P2 Directory")
    LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    _, selected = PilotBatchSelectionService(session).build(campaign.slug, "Batch 1", limit=1, commit=True)
    assert len(selected) == 1
    row = session.query(PilotBatchCandidate).one()
    assert row.priority_tier in {PriorityTier.P1_BEST_PILOT, PriorityTier.P2_GOOD_WITH_CAUTION}


def test_idempotent_batch_build(session):
    campaign, _ = make_phase5_candidate(session)
    LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    PilotBatchSelectionService(session).build(campaign.slug, "Batch Idem", limit=5, commit=True)
    PilotBatchSelectionService(session).build(campaign.slug, "Batch Idem", limit=5, commit=True)
    assert session.query(PilotBatchCandidate).filter_by(batch_name="Batch Idem").count() == 1
