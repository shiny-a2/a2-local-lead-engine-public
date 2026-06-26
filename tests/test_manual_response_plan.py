from app.db.models.manual_response_plan import ManualResponsePlan
from tests.phase12_helpers import build_opportunity_from_body


def test_response_plan_created_with_avoid_claims(session):
    build_opportunity_from_body(session, "yes interested")
    plan = session.query(ManualResponsePlan).first()
    assert plan.manual_notes_required is True
    assert "final price quote" in plan.claims_to_avoid_json["avoid"]
    assert "booking/enquiry" in plan.modules_to_mention_json["modules"]
