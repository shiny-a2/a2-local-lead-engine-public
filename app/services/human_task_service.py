from sqlalchemy.orm import Session

from app.core.enums import (
    HumanResponseTaskType,
    HumanTaskPriority,
    HumanTaskStatus,
    LeadResponseTimelineEventType,
    ReplyClassificationValue,
)
from app.db.models.human_response_task import HumanResponseTask
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.lead_response_timeline import LeadResponseTimeline
from app.db.models.reply_classification import ReplyClassification
from app.settings import Settings


class HumanTaskService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create_for_classification(
        self, message: InboundEmailMessage, classification: ReplyClassification
    ) -> HumanResponseTask | None:
        if not self.settings.phase11_create_human_tasks:
            return None
        if message.matched_candidate_business_id is None:
            return None
        task_map = {
            ReplyClassificationValue.POSITIVE_INTEREST: (
                HumanResponseTaskType.REVIEW_POSITIVE_REPLY,
                HumanTaskPriority.HIGH,
            ),
            ReplyClassificationValue.ASKING_PRICE: (
                HumanResponseTaskType.SEND_PRICE_INFO,
                HumanTaskPriority.HIGH,
            ),
            ReplyClassificationValue.ASKING_DETAILS: (
                HumanResponseTaskType.REPLY_MANUALLY,
                HumanTaskPriority.MEDIUM,
            ),
            ReplyClassificationValue.REQUESTED_CALL: (
                HumanResponseTaskType.CALL_REQUESTED_MANUAL,
                HumanTaskPriority.HIGH,
            ),
            ReplyClassificationValue.UNKNOWN_NEEDS_REVIEW: (
                HumanResponseTaskType.REVIEW_UNKNOWN_REPLY,
                HumanTaskPriority.MEDIUM,
            ),
            ReplyClassificationValue.BOUNCE_LIKE: (
                HumanResponseTaskType.REVIEW_BOUNCE,
                HumanTaskPriority.MEDIUM,
            ),
        }
        task_data = task_map.get(classification.classification)
        if task_data is None:
            return None
        task = HumanResponseTask(
            candidate_business_id=message.matched_candidate_business_id,
            inbound_message_id=message.id,
            task_type=task_data[0],
            priority=task_data[1],
            status=HumanTaskStatus.OPEN,
            notes="Phase 11 task only. No outbound message was generated.",
        )
        self.session.add(task)
        self.session.add(
            LeadResponseTimeline(
                candidate_business_id=message.matched_candidate_business_id,
                event_type=LeadResponseTimelineEventType.TASK_CREATED,
                event_source="phase11",
                event_summary=f"Human task created: {task.task_type.value}",
                related_inbound_message_id=message.id,
            )
        )
        self.session.flush()
        return task
