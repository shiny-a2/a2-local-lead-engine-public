from app.core.enums import FutureEmailBlockType
from app.db.models.candidate_economic_value_angle import CandidateEconomicValueAngle
from app.db.models.candidate_offer_match import CandidateOfferMatch
from app.db.models.future_email_offer_block import FutureEmailOfferBlock


class FutureEmailBlockService:
    forbidden_full_email_markers = ["subject:", "hi ", "hello ", "regards", "cheers"]

    def build(
        self,
        candidate_id: int,
        insight_run_id: int,
        offer: CandidateOfferMatch,
        angles: list[CandidateEconomicValueAngle],
    ) -> list[FutureEmailOfferBlock]:
        blocks = [
            FutureEmailOfferBlock(
                candidate_business_id=candidate_id,
                insight_run_id=insight_run_id,
                block_type=FutureEmailBlockType.OFFER_MODULE_BLOCK,
                block_text=offer.email_safe_offer_summary,
                allowed_for_phase7=True,
                requires_judge=True,
                risk_flags_json=[],
                supporting_evidence_json={"offer_match_id": "pending"},
            )
        ]
        for angle in angles:
            blocks.append(
                FutureEmailOfferBlock(
                    candidate_business_id=candidate_id,
                    insight_run_id=insight_run_id,
                    block_type=FutureEmailBlockType.ECONOMIC_VALUE_BLOCK,
                    block_text=angle.angle_text,
                    allowed_for_phase7=angle.allowed_for_future_copy,
                    requires_judge=True,
                    risk_flags_json=[],
                    supporting_evidence_json={"angle_type": angle.angle_type.value},
                )
            )
        return blocks
