from sqlalchemy import select

from app.core.enums import ScopeChecklistType
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.scope_checklist_item import ScopeChecklistItem
from app.services.scope_checklist_service import ScopeChecklistService
from tests.phase12_helpers import build_opportunity_from_body


def _checklist_for_category(session, category):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    candidate = session.get(CandidateBusiness, opportunity.candidate_business_id)
    candidate.canonical_category = category
    checklist = ScopeChecklistService(session).create_for_opportunity(opportunity)
    session.flush()
    return checklist


def test_beauty_salon_checklist_created(session):
    assert _checklist_for_category(session, "beauty_salon").checklist_type == ScopeChecklistType.BEAUTY_SALON_BOOKING_SCOPE


def test_barber_checklist_created(session):
    assert _checklist_for_category(session, "barber").checklist_type == ScopeChecklistType.BARBER_DIRECT_BOOKING_SCOPE


def test_cleaning_checklist_created(session):
    assert _checklist_for_category(session, "cleaning_service").checklist_type == ScopeChecklistType.CLEANING_QUOTE_REQUEST_SCOPE


def test_cafe_checklist_created_when_category_exists(session):
    assert _checklist_for_category(session, "cafe").checklist_type == ScopeChecklistType.CAFE_MENU_QR_SCOPE


def test_required_questions_tracked(session):
    checklist = _checklist_for_category(session, "beauty_salon")
    items = session.scalars(select(ScopeChecklistItem).where(ScopeChecklistItem.scope_checklist_id == checklist.id)).all()
    assert any(item.required for item in items)
    assert any(item.item_key == "services_count" for item in items)
