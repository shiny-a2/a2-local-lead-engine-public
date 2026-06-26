from sqlalchemy import select

from app.core.enums import ChecklistItemStatus
from app.db.models.scope_checklist_item import ScopeChecklistItem
from app.services.scope_checklist_service import ScopeChecklistService
from app.services.scope_completeness_service import ScopeCompletenessService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_incomplete_scope_blocks_quote_readiness(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    checklist = ScopeChecklistService(session).create_for_opportunity(opportunity)
    score = ScopeCompletenessService(session, Settings(testing=True)).calculate(checklist)
    assert score == 0
    assert checklist.quote_ready is False


def test_completed_required_scope_allows_worksheet_readiness(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    checklist = ScopeChecklistService(session).create_for_opportunity(opportunity)
    items = session.scalars(select(ScopeChecklistItem).where(ScopeChecklistItem.scope_checklist_id == checklist.id)).all()
    for item in items:
        if item.required:
            item.status = ChecklistItemStatus.ANSWERED
            item.answer_text = "ready"
    score = ScopeCompletenessService(session, Settings(testing=True)).calculate(checklist)
    assert score == 100
    assert checklist.quote_ready is True
