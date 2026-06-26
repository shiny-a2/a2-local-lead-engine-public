from datetime import UTC, datetime, timedelta

from app.core.enums import NextHumanActionType, SalesTaskStatus
from app.db.models.sales_task import SalesTask
from app.services.next_human_action_service import NextHumanActionService
from app.services.opportunity_health_service import OpportunityHealthService
from app.services.sales_task_service import SalesTaskService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_price_request_creates_scope_or_manual_quote_action(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "what is the price?")
    action = NextHumanActionService(session).create(opportunity)
    assert action.action_type == NextHumanActionType.ASK_SCOPE_QUESTIONS


def test_call_request_creates_manual_call(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "call me please")
    action = NextHumanActionService(session).create(opportunity)
    assert action.action_type == NextHumanActionType.MANUAL_CALL


def test_stale_opportunity_creates_at_risk_health(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    SalesTaskService(session, Settings(testing=True)).create_initial_tasks(opportunity)
    task = session.query(SalesTask).filter_by(opportunity_id=opportunity.id).one()
    task.due_at = datetime.now(UTC) - timedelta(days=4)
    task.status = SalesTaskStatus.OPEN
    snapshot = OpportunityHealthService(session).snapshot(opportunity)
    assert snapshot.health_status.value == "AT_RISK_STALE"
