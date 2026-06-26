from sqlalchemy import select

from app.core.enums import ChecklistItemStatus, OpportunityCloseReason
from app.db.models.scope_checklist_item import ScopeChecklistItem
from app.services.opportunity_close_service import OpportunityCloseService
from app.services.opportunity_health_service import OpportunityHealthService
from app.services.scope_checklist_service import ScopeChecklistService
from app.services.scope_completeness_service import ScopeCompletenessService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_completed_scope_improves_health(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    checklist = ScopeChecklistService(session).create_for_opportunity(opportunity)
    for item in session.scalars(select(ScopeChecklistItem).where(ScopeChecklistItem.scope_checklist_id == checklist.id)):
        if item.required:
            item.status = ChecklistItemStatus.ANSWERED
            item.answer_text = "ready"
    ScopeCompletenessService(session, Settings(testing=True)).calculate(checklist)
    snapshot = OpportunityHealthService(session).snapshot(opportunity)
    assert snapshot.health_status.value == "HEALTHY"


def test_closed_opportunity_health_closed(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    OpportunityCloseService(session).close(opportunity, OpportunityCloseReason.MANUAL_DECISION, "Amirali")
    snapshot = OpportunityHealthService(session).snapshot(opportunity)
    assert snapshot.health_status.value == "CLOSED"
