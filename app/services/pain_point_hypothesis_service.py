from app.core.enums import CampaignLane, PainPointType
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_pain_point_hypothesis import CandidatePainPointHypothesis


class PainPointHypothesisService:
    def build(self, candidate: CandidateBusiness, insight_run_id: int, lane: CampaignLane) -> list[CandidatePainPointHypothesis]:
        pain_type = {
            CampaignLane.NO_WEBSITE: PainPointType.NO_DEDICATED_WEBSITE,
            CampaignLane.SOCIAL_ONLY: PainPointType.SOCIAL_ONLY_PRESENCE,
            CampaignLane.DIRECTORY_ONLY: PainPointType.DIRECTORY_ONLY_PRESENCE,
        }.get(lane, PainPointType.UNCLEAR_CUSTOMER_ACTION_PATH)
        return [
            CandidatePainPointHypothesis(
                candidate_business_id=candidate.id,
                insight_run_id=insight_run_id,
                pain_point_type=pain_type,
                pain_point_text="The direct customer action path may be less clear than it could be.",
                confidence=0.65,
                evidence_json={"campaign_lane": lane.value},
                requires_verification=True,
                allowed_for_future_copy=pain_type
                in {
                    PainPointType.NO_DEDICATED_WEBSITE,
                    PainPointType.SOCIAL_ONLY_PRESENCE,
                    PainPointType.DIRECTORY_ONLY_PRESENCE,
                },
            )
        ]
