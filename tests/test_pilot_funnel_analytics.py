from app.db.models.candidate_business import CandidateBusiness
from app.services.pilot_funnel_analytics_service import PilotFunnelAnalyticsService
from tests.phase14_helpers import make_campaign


def test_pilot_funnel_counts_candidates(session):
    campaign = make_campaign(session)
    session.add(
        CandidateBusiness(
            candidate_identity_fingerprint="a",
            canonical_name="A",
            display_name="A",
            normalized_name="a",
            canonical_category="barber",
            city="Auckland",
            country="New Zealand",
        )
    )
    session.flush()
    snapshot = PilotFunnelAnalyticsService(session).snapshot(campaign.id)
    assert snapshot["candidates"] == 1
    assert snapshot["sent_to_provider"] == 0
