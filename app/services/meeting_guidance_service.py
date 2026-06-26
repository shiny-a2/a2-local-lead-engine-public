from sqlalchemy.orm import Session

from app.db.models.meeting_guidance_record import MeetingGuidanceRecord
from app.db.models.opportunity_record import OpportunityRecord


class MeetingGuidanceService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, opportunity: OpportunityRecord, requested: bool = False) -> MeetingGuidanceRecord:
        row = MeetingGuidanceRecord(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            inbound_message_id=opportunity.source_inbound_message_id,
            meeting_requested=requested,
            automatic_scheduling_allowed=False,
            recommended_action="Human should manually decide whether to offer a call.",
            suggested_questions_json={
                "questions": [
                    "What outcome would make the call useful?",
                    "What scope details are missing?",
                    "Is this worth preparing before a manual call?",
                ]
            },
            manual_owner="Amirali",
        )
        self.session.add(row)
        self.session.flush()
        return row
