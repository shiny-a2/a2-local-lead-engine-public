from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import Actor, CampaignStatus
from app.db.models.campaign import Campaign
from app.services.audit_service import AuditService
from app.settings import Settings

SEED_CAMPAIGN_SLUG = "auckland-local-website-pilot"


def seed_initial_campaign(
    session: Session, settings: Settings, run_id: str | None = None
) -> tuple[Campaign, bool]:
    existing = session.scalar(select(Campaign).where(Campaign.slug == SEED_CAMPAIGN_SLUG))
    if existing:
        return existing, False

    campaign = Campaign(
        name="Auckland Local Website Pilot",
        slug=SEED_CAMPAIGN_SLUG,
        target_city="Auckland",
        target_country="New Zealand",
        target_categories_json=["barber", "beauty_salon", "cleaning_service"],
        daily_send_limit=10,
        manual_approval_required=True,
        status=CampaignStatus.DRAFT,
    )
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    AuditService(session, settings).record(
        entity_type="campaign",
        entity_id=str(campaign.id),
        action="seed_initial_campaign",
        actor=Actor.CLI,
        run_id=run_id,
        after={"slug": campaign.slug, "status": campaign.status.value},
    )
    return campaign, True
