from sqlalchemy.orm import Session

from app.core.enums import PricingStrategy
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.pricing_guidance_record import PricingGuidanceRecord


class PricingGuidanceService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, opportunity: OpportunityRecord) -> PricingGuidanceRecord:
        row = PricingGuidanceRecord(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            inbound_message_id=opportunity.source_inbound_message_id,
            pricing_strategy=PricingStrategy.ASK_SCOPE_FIRST,
            internal_price_band="internal_only_manual_estimate",
            show_price_to_user=False,
            manual_quote_required=True,
            scope_questions_json={
                "questions": [
                    "What pages or sections are needed?",
                    "Is booking, quote request, or menu management required?",
                    "Is this a lightweight starter version or broader project?",
                ]
            },
            pricing_notes_json={"guidance_only": True, "final_quote_generated": False},
            blocked_price_claims_json={
                "blocked": ["fixed final quote", "guaranteed savings", "automatic discount"]
            },
        )
        self.session.add(row)
        self.session.flush()
        return row
