from app.db.models.meeting_guidance_record import MeetingGuidanceRecord
from tests.phase12_helpers import build_opportunity_from_body


def test_call_request_creates_manual_meeting_guidance(session):
    build_opportunity_from_body(session, "call me please")
    guidance = session.query(MeetingGuidanceRecord).first()
    assert guidance.meeting_requested is True
    assert guidance.automatic_scheduling_allowed is False
    assert "manual" in guidance.recommended_action.lower()
