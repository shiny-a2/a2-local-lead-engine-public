from app.core.enums import OpportunityStatus
from app.db.models.candidate_business import CandidateBusiness
from app.services.sales_workspace_service import SalesWorkspaceService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def build_phase13_workspace(session, body: str = "yes interested", category: str = "beauty_salon"):
    campaign, _, _, opportunity = build_opportunity_from_body(session, body)
    candidate = session.get(CandidateBusiness, opportunity.candidate_business_id)
    if candidate:
        candidate.canonical_category = category
    if opportunity.opportunity_status == OpportunityStatus.CLOSED_NOT_INTERESTED:
        session.flush()
        return campaign, opportunity
    SalesWorkspaceService(session, Settings(testing=True)).build_for_campaign(campaign.slug, True)
    session.flush()
    return campaign, opportunity
