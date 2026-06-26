import pytest

from app.core.enums import PricingWorksheetStatus
from app.services.internal_pricing_worksheet_service import InternalPricingWorksheetService
from tests.phase12_helpers import build_opportunity_from_body


def test_worksheet_created(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "what is the price?")
    worksheet = InternalPricingWorksheetService(session).create_for_opportunity(opportunity)
    assert worksheet.pricing_status == PricingWorksheetStatus.NEEDS_SCOPE


def test_no_automatic_final_quote(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "what is the price?")
    worksheet = InternalPricingWorksheetService(session).create_for_opportunity(opportunity)
    assert worksheet.final_manual_quote is None


def test_final_quote_only_human_entered_and_approval_required(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "what is the price?")
    service = InternalPricingWorksheetService(session)
    service.create_for_opportunity(opportunity)
    with pytest.raises(ValueError):
        service.approve_manually(opportunity.id, "Amirali")
    service.update_manual_price(opportunity.id, 1200, "manual only")
    worksheet = service.approve_manually(opportunity.id, "Amirali")
    assert worksheet.final_manual_quote == 1200
    assert worksheet.quote_approved_by == "Amirali"
