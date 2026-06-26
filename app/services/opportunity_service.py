from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    OpportunityAuditAction,
    OpportunityStatus,
    OpportunityType,
    Phase12DecisionValue,
    ReplyClassificationValue,
)
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.opportunity_audit_event import OpportunityAuditEvent
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase12_decision import Phase12Decision
from app.db.models.reply_classification import ReplyClassification
from app.services.followup_eligibility_service import FollowupEligibilityService
from app.services.human_sales_control_gate_service import HumanSalesControlGateService
from app.services.meeting_guidance_service import MeetingGuidanceService
from app.services.phase12_task_service import Phase12TaskService
from app.services.pricing_guidance_service import PricingGuidanceService
from app.services.reply_draft_suggestion_service import ReplyDraftSuggestionService
from app.services.response_guidance_service import ResponseGuidanceService
from app.settings import Settings


class OpportunityService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def build_for_campaign(self, campaign_slug: str, commit: bool) -> dict:
        classifications = self.session.scalars(select(ReplyClassification)).all()
        created = closed = tasks = pricing = meetings = 0
        if not commit:
            return {
                "opportunities_created": 0,
                "closed": 0,
                "tasks": 0,
                "pricing_guidance": 0,
                "meeting_guidance": 0,
                "dry_run": True,
            }
        for classification in classifications:
            message = self.session.get(InboundEmailMessage, classification.inbound_message_id)
            if message is None or message.matched_candidate_business_id is None:
                continue
            queue = self.session.get(EmailSendQueue, message.matched_send_queue_id) if message.matched_send_queue_id else None
            if queue is None:
                continue
            opp = self.create_from_reply(message, classification, queue.campaign_id)
            if opp.opportunity_status.name.startswith("CLOSED"):
                closed += 1
            else:
                created += 1
            if opp.opportunity_status == OpportunityStatus.ASKED_PRICE:
                pricing += 1
            if opp.opportunity_status == OpportunityStatus.CALL_REQUESTED:
                meetings += 1
            tasks += 1
        return {
            "opportunities_created": created,
            "closed": closed,
            "tasks": tasks,
            "pricing_guidance": pricing,
            "meeting_guidance": meetings,
            "dry_run": False,
        }

    def create_from_reply(
        self,
        message: InboundEmailMessage,
        classification: ReplyClassification,
        campaign_id: int,
    ) -> OpportunityRecord:
        existing = self.session.scalar(
            select(OpportunityRecord).where(
                OpportunityRecord.source_inbound_message_id == message.id
            )
        )
        if existing:
            return existing
        status = self._status(classification.classification)
        opp = OpportunityRecord(
            candidate_business_id=message.matched_candidate_business_id or 0,
            campaign_id=campaign_id,
            source_inbound_message_id=message.id,
            opportunity_status=status,
            opportunity_type=self._type(status),
            priority="HIGH" if status in {OpportunityStatus.ASKED_PRICE, OpportunityStatus.CALL_REQUESTED} else "MEDIUM",
            estimated_value_band="internal_only",
            confidence=classification.confidence,
        )
        self.session.add(opp)
        self.session.flush()
        HumanSalesControlGateService(self.session, self.settings).apply(opp)
        ResponseGuidanceService(self.session).create(opp)
        PricingGuidanceService(self.session).create(opp)
        MeetingGuidanceService(self.session).create(opp, status == OpportunityStatus.CALL_REQUESTED)
        FollowupEligibilityService(self.session, self.settings).create(opp)
        Phase12TaskService(self.session, self.settings).create(opp)
        ReplyDraftSuggestionService(self.session, self.settings).create_optional(opp)
        self.session.add(
            Phase12Decision(
                candidate_business_id=opp.candidate_business_id,
                opportunity_id=opp.id,
                inbound_message_id=message.id,
                decision=self._decision(status),
                ready_for_phase13=False,
                manual_action_required=not status.name.startswith("CLOSED"),
                closed=status.name.startswith("CLOSED"),
                reason="Manual opportunity planning only; no outbound action.",
            )
        )
        self.session.add(
            OpportunityAuditEvent(
                opportunity_id=opp.id,
                candidate_business_id=opp.candidate_business_id,
                actor="system",
                action=OpportunityAuditAction.OPPORTUNITY_CREATED,
                reason="Created from Phase 11 classification",
            )
        )
        return opp

    def _status(self, value: ReplyClassificationValue) -> OpportunityStatus:
        return {
            ReplyClassificationValue.POSITIVE_INTEREST: OpportunityStatus.QUALIFIED_INTEREST,
            ReplyClassificationValue.ASKING_PRICE: OpportunityStatus.ASKED_PRICE,
            ReplyClassificationValue.ASKING_DETAILS: OpportunityStatus.ASKED_DETAILS,
            ReplyClassificationValue.REQUESTED_CALL: OpportunityStatus.CALL_REQUESTED,
            ReplyClassificationValue.NOT_INTERESTED: OpportunityStatus.CLOSED_NOT_INTERESTED,
            ReplyClassificationValue.WRONG_CONTACT: OpportunityStatus.CLOSED_WRONG_CONTACT,
            ReplyClassificationValue.UNSUBSCRIBE_REQUEST: OpportunityStatus.CLOSED_UNSUBSCRIBED,
            ReplyClassificationValue.BOUNCE_LIKE: OpportunityStatus.CLOSED_BOUNCED,
        }.get(value, OpportunityStatus.NEEDS_MANUAL_RESPONSE)

    def _type(self, status: OpportunityStatus) -> OpportunityType:
        if status == OpportunityStatus.ASKED_PRICE:
            return OpportunityType.WEBSITE_PROJECT
        if status == OpportunityStatus.CALL_REQUESTED:
            return OpportunityType.BOOKING_SYSTEM
        if status == OpportunityStatus.ASKED_DETAILS:
            return OpportunityType.QUOTE_REQUEST_SITE
        return OpportunityType.UNKNOWN

    def _decision(self, status: OpportunityStatus) -> Phase12DecisionValue:
        if status == OpportunityStatus.ASKED_PRICE:
            return Phase12DecisionValue.PRICE_RESPONSE_GUIDANCE_READY
        if status == OpportunityStatus.CALL_REQUESTED:
            return Phase12DecisionValue.CALL_REQUEST_TASK_CREATED
        if status == OpportunityStatus.CLOSED_NOT_INTERESTED:
            return Phase12DecisionValue.CLOSED_NOT_INTERESTED
        if status == OpportunityStatus.CLOSED_WRONG_CONTACT:
            return Phase12DecisionValue.CLOSED_WRONG_CONTACT
        if status in {OpportunityStatus.CLOSED_UNSUBSCRIBED, OpportunityStatus.CLOSED_BOUNCED}:
            return Phase12DecisionValue.CLOSED_SUPPRESSED
        return Phase12DecisionValue.OPPORTUNITY_CREATED
