from app.services.business_insight_orchestrator_service import BusinessInsightOrchestratorService
from tests.phase6_helpers import make_phase6_ready_candidate


def make_phase7_ready_candidate(session, category="barber"):
    campaign, candidate = make_phase6_ready_candidate(session, category=category)
    BusinessInsightOrchestratorService(session).run(campaign.slug, commit=True)
    return campaign, candidate
