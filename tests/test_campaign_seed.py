from sqlalchemy import select

from app.db.models.campaign import Campaign
from app.services.campaign_service import seed_initial_campaign


def test_campaign_seed_creates_campaign(session, test_settings):
    campaign, created = seed_initial_campaign(session, test_settings, "run-test")
    assert created is True
    assert campaign.slug == "auckland-local-website-pilot"


def test_campaign_seed_is_idempotent(session, test_settings):
    seed_initial_campaign(session, test_settings, "run-test")
    seed_initial_campaign(session, test_settings, "run-test")
    campaigns = session.scalars(select(Campaign)).all()
    assert len(campaigns) == 1

