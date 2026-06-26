from app.core.enums import FollowupType
from app.db.models.followup_eligibility_record import FollowupEligibilityRecord
from tests.phase12_helpers import build_opportunity_from_body


def test_positive_followup_manual_only(session):
    build_opportunity_from_body(session, "yes interested")
    row = session.query(FollowupEligibilityRecord).first()
    assert row.eligible is True
    assert row.followup_type == FollowupType.MANUAL_ONLY


def test_negative_followup_not_allowed(session):
    build_opportunity_from_body(session, "not interested")
    row = session.query(FollowupEligibilityRecord).first()
    assert row.eligible is False
    assert row.followup_type == FollowupType.NOT_ALLOWED
