from sqlalchemy import select

from app.db.models.sales_workspace_item import SalesWorkspaceItem
from app.services.sales_workspace_service import SalesWorkspaceService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_opportunities_create_workspace_items(session):
    campaign, _, _, _ = build_opportunity_from_body(session, "yes interested")
    summary = SalesWorkspaceService(session, Settings(testing=True)).build_for_campaign(campaign.slug, True)
    assert summary["workspace_item_count"] == 1
    assert session.scalar(select(SalesWorkspaceItem)) is not None


def test_closed_leads_excluded(session):
    campaign, _, _, _ = build_opportunity_from_body(session, "not interested")
    summary = SalesWorkspaceService(session, Settings(testing=True)).build_for_campaign(campaign.slug, True)
    assert summary["workspace_item_count"] == 0


def test_workspace_build_idempotent(session):
    campaign, _, _, _ = build_opportunity_from_body(session, "yes interested")
    service = SalesWorkspaceService(session, Settings(testing=True))
    service.build_for_campaign(campaign.slug, True)
    service.build_for_campaign(campaign.slug, True)
    assert len(session.scalars(select(SalesWorkspaceItem)).all()) == 1
