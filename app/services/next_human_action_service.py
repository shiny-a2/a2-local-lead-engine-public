from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.enums import (
    HumanTaskPriority,
    NextHumanActionStatus,
    NextHumanActionType,
    OpportunityStatus,
)
from app.db.models.next_human_action import NextHumanAction
from app.db.models.opportunity_record import OpportunityRecord


class NextHumanActionService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, opportunity: OpportunityRecord) -> NextHumanAction:
        action_type = self._action_type(opportunity)
        action = NextHumanAction(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            action_type=action_type,
            priority=HumanTaskPriority.HIGH
            if action_type in {NextHumanActionType.PREPARE_MANUAL_QUOTE, NextHumanActionType.MANUAL_CALL}
            else HumanTaskPriority.MEDIUM,
            reason="Recommended next human action only; no automation is performed.",
            due_at=datetime.now(UTC) + timedelta(hours=24),
            status=NextHumanActionStatus.OPEN,
        )
        self.session.add(action)
        return action

    def _action_type(self, opportunity: OpportunityRecord) -> NextHumanActionType:
        if opportunity.opportunity_status == OpportunityStatus.ASKED_PRICE:
            return NextHumanActionType.ASK_SCOPE_QUESTIONS
        if opportunity.opportunity_status == OpportunityStatus.CALL_REQUESTED:
            return NextHumanActionType.MANUAL_CALL
        if opportunity.opportunity_status == OpportunityStatus.ASKED_DETAILS:
            return NextHumanActionType.REVIEW_PROPOSAL_CHECKLIST
        if opportunity.opportunity_status.name.startswith("CLOSED"):
            return NextHumanActionType.CLOSE_OPPORTUNITY
        return NextHumanActionType.PREPARE_MANUAL_REPLY
