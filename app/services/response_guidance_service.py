from sqlalchemy.orm import Session

from app.core.enums import OpportunityStatus, ResponseGuidanceType
from app.db.models.manual_response_plan import ManualResponsePlan
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.response_guidance_record import ResponseGuidanceRecord


class ResponseGuidanceService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, opportunity: OpportunityRecord) -> tuple[ManualResponsePlan, ResponseGuidanceRecord]:
        response_type = {
            OpportunityStatus.ASKED_PRICE: ResponseGuidanceType.PRICE_RESPONSE_GUIDANCE,
            OpportunityStatus.ASKED_DETAILS: ResponseGuidanceType.DETAILS_RESPONSE_GUIDANCE,
            OpportunityStatus.CALL_REQUESTED: ResponseGuidanceType.CALL_RESPONSE_GUIDANCE,
            OpportunityStatus.QUALIFIED_INTEREST: ResponseGuidanceType.POSITIVE_INTEREST_RESPONSE_GUIDANCE,
            OpportunityStatus.CLOSED_NOT_INTERESTED: ResponseGuidanceType.NEGATIVE_REPLY_CLOSURE_GUIDANCE,
            OpportunityStatus.CLOSED_WRONG_CONTACT: ResponseGuidanceType.WRONG_CONTACT_GUIDANCE,
        }.get(opportunity.opportunity_status, ResponseGuidanceType.POSITIVE_INTEREST_RESPONSE_GUIDANCE)
        avoid = {
            "avoid": [
                "final price quote",
                "meeting link",
                "send-ready response",
                "guaranteed results",
                "pressure language",
            ]
        }
        guidance = ResponseGuidanceRecord(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            inbound_message_id=opportunity.source_inbound_message_id,
            response_type=response_type,
            response_goal="Help Amirali prepare a manual, specific response.",
            key_points_json={"points": ["acknowledge reply", "ask scope", "keep tone calm"]},
            things_to_avoid_json=avoid,
            recommended_tone="calm, helpful, human",
            cta_recommendation="Manual next step only; do not send automatically.",
            manual_review_required=True,
        )
        plan = ManualResponsePlan(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            inbound_message_id=opportunity.source_inbound_message_id,
            response_goal=guidance.response_goal,
            recommended_tone=guidance.recommended_tone,
            key_points_json=guidance.key_points_json,
            claims_allowed_json={"allowed": ["can mention original offer context"]},
            claims_to_avoid_json=avoid,
            offer_package=opportunity.opportunity_type.value,
            modules_to_mention_json={"modules": ["booking/enquiry", "quote request", "simple site"]},
            pricing_strategy="ASK_SCOPE_FIRST",
            cta_suggestion="Ask one or two scope questions manually.",
            manual_notes_required=True,
        )
        self.session.add_all([guidance, plan])
        self.session.flush()
        return plan, guidance
