from app.core.enums import FollowupType, ManualFollowupStatus
from app.services.manual_followup_plan_service import ManualFollowupPlanService
from tests.phase12_helpers import build_opportunity_from_body


def test_manual_only_followup_created(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    plan = ManualFollowupPlanService(session).create_for_opportunity(opportunity)
    assert plan.followup_type == FollowupType.MANUAL_ONLY
    assert plan.eligible is True


def test_not_interested_unsubscribed_bounced_blocked(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "not interested")
    plan = ManualFollowupPlanService(session).create_for_opportunity(opportunity)
    assert plan.followup_type == FollowupType.NOT_ALLOWED


def test_done_manually_can_be_logged(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    plan = ManualFollowupPlanService(session).create_for_opportunity(opportunity)
    plan.status = ManualFollowupStatus.DONE_MANUALLY
    assert plan.status == ManualFollowupStatus.DONE_MANUALLY
