from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import FollowupType, ManualFollowupStatus, OpportunityStatus
from app.db.models.manual_followup_plan import ManualFollowupPlan
from app.db.models.opportunity_record import OpportunityRecord


class ManualFollowupPlanService:
    def __init__(self, session: Session):
        self.session = session

    def create_for_opportunity(self, opportunity: OpportunityRecord) -> ManualFollowupPlan:
        existing = self.session.scalar(
            select(ManualFollowupPlan).where(ManualFollowupPlan.opportunity_id == opportunity.id)
        )
        if existing:
            return existing
        closed_or_blocked = opportunity.opportunity_status in {
            OpportunityStatus.CLOSED_BOUNCED,
            OpportunityStatus.CLOSED_NOT_INTERESTED,
            OpportunityStatus.CLOSED_UNSUBSCRIBED,
            OpportunityStatus.CLOSED_WRONG_CONTACT,
        }
        plan = ManualFollowupPlan(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            eligible=not closed_or_blocked,
            followup_type=FollowupType.NOT_ALLOWED if closed_or_blocked else FollowupType.MANUAL_ONLY,
            not_before=None if closed_or_blocked else datetime.now(UTC) + timedelta(days=3),
            reason=(
                "Closed/suppressed/bounced opportunities are not follow-up eligible."
                if closed_or_blocked
                else "Manual follow-up planning only; no automatic scheduling or sending."
            ),
            status=ManualFollowupStatus.BLOCKED if closed_or_blocked else ManualFollowupStatus.PLANNED,
        )
        self.session.add(plan)
        self.session.flush()
        return plan
