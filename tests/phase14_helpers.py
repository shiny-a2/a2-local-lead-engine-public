from app.core.enums import CampaignStatus
from app.db.models.campaign import Campaign


def make_campaign(session, slug: str = "auckland-local-website-pilot") -> Campaign:
    campaign = Campaign(
        slug=slug,
        name="Auckland Pilot",
        target_country="New Zealand",
        target_city="Auckland",
        target_categories_json=["barber"],
        status=CampaignStatus.DRAFT,
    )
    session.add(campaign)
    session.flush()
    return campaign
