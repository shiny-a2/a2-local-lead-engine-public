from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import HumanTaskPriority, OpportunityStatus, SalesTaskStatus, SalesTaskType
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.sales_task import SalesTask
from app.settings import Settings


class SalesTaskService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create_initial_tasks(self, opportunity: OpportunityRecord) -> list[SalesTask]:
        existing = self.session.scalars(
            select(SalesTask).where(SalesTask.opportunity_id == opportunity.id)
        ).all()
        if existing:
            return list(existing)
        task_type = self._task_type(opportunity)
        task = SalesTask(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            task_type=task_type,
            priority=HumanTaskPriority.HIGH
            if opportunity.opportunity_status
            in {OpportunityStatus.ASKED_PRICE, OpportunityStatus.CALL_REQUESTED}
            else HumanTaskPriority.MEDIUM,
            status=SalesTaskStatus.OPEN,
            due_at=datetime.now(UTC) + timedelta(hours=24),
            title=f"Manual action: {task_type.value}",
            description="Human-only sales workspace task. No outbound action is automated.",
        )
        self.session.add(task)
        self.session.flush()
        return [task]

    def _task_type(self, opportunity: OpportunityRecord) -> SalesTaskType:
        if opportunity.opportunity_status == OpportunityStatus.ASKED_PRICE:
            return SalesTaskType.ASK_SCOPE_QUESTIONS
        if opportunity.opportunity_status == OpportunityStatus.CALL_REQUESTED:
            return SalesTaskType.MANUAL_CALL
        if opportunity.opportunity_status == OpportunityStatus.ASKED_DETAILS:
            return SalesTaskType.PREPARE_PROPOSAL_CHECKLIST
        return SalesTaskType.MANUAL_REPLY
