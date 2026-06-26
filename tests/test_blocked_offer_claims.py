from app.db.models.blocked_offer_claim import BlockedOfferClaim
from app.db.models.future_email_offer_block import FutureEmailOfferBlock
from app.services.business_insight_orchestrator_service import BusinessInsightOrchestratorService
from tests.phase6_helpers import make_phase6_ready_candidate


def test_blocked_claims_are_stored_and_not_allowed_blocks(session):
    campaign, _ = make_phase6_ready_candidate(session)
    run = BusinessInsightOrchestratorService(session).run(campaign.slug, commit=True)
    claims = session.query(BlockedOfferClaim).filter_by(insight_run_id=run.id).all()
    assert claims
    blocks = session.query(FutureEmailOfferBlock).filter_by(insight_run_id=run.id).all()
    assert all("guaranteed" not in block.block_text.lower() for block in blocks)
