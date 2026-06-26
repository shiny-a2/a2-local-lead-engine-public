from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.enums import HumanTaskPriority, HumanTaskStatus, OpportunityStatus, Phase12TaskType
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase12_human_task import Phase12HumanTask
from app.settings import Settings


class Phase12TaskService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create(self, opportunity: OpportunityRecord) -> Phase12HumanTask:
        task_type = {
            OpportunityStatus.ASKED_PRICE: Phase12TaskType.PREPARE_PRICE_RESPONSE,
            OpportunityStatus.ASKED_DETAILS: Phase12TaskType.VERIFY_SCOPE,
            OpportunityStatus.CALL_REQUESTED: Phase12TaskType.SCHEDULE_MANUAL_CALL,
            OpportunityStatus.CLOSED_NOT_INTERESTED: Phase12TaskType.CLOSE_LEAD,
            OpportunityStatus.CLOSED_WRONG_CONTACT: Phase12TaskType.CLOSE_LEAD,
            OpportunityStatus.CLOSED_UNSUBSCRIBED: Phase12TaskType.SUPPRESS_CONTACT,
            OpportunityStatus.CLOSED_BOUNCED: Phase12TaskType.SUPPRESS_CONTACT,
        }.get(opportunity.opportunity_status, Phase12TaskType.PREPARE_REPLY)
        task = Phase12HumanTask(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            inbound_message_id=opportunity.source_inbound_message_id,
            task_type=task_type,
            priority=HumanTaskPriority.HIGH
            if opportunity.opportunity_status
            in {OpportunityStatus.ASKED_PRICE, OpportunityStatus.CALL_REQUESTED}
            else HumanTaskPriority.MEDIUM,
            status=HumanTaskStatus.OPEN,
            due_at=datetime.now(UTC) + timedelta(hours=self.settings.phase12_default_task_due_hours),
            recommended_action="Human action required. Do not send automatically.",
            notes="Phase 12 task only; no outbound action.",
        )
        self.session.add(task)
        self.session.flush()
        return task
