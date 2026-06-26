from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.campaign import Campaign
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


@router.get("/campaigns")
def campaigns() -> list[dict[str, object]]:
    settings = get_settings()
    session_factory = make_session_factory(settings)
    with session_factory() as session:
        rows = session.scalars(select(Campaign).order_by(Campaign.id)).all()
        return [
            {
                "id": campaign.id,
                "name": campaign.name,
                "slug": campaign.slug,
                "status": campaign.status.value,
                "daily_send_limit": campaign.daily_send_limit,
                "manual_approval_required": campaign.manual_approval_required,
            }
            for campaign in rows
        ]

