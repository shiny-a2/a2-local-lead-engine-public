from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_business_insight import CandidateBusinessInsight


class BusinessInsightService:
    def build(self, candidate: CandidateBusiness, insight_run_id: int, campaign_lane: str) -> CandidateBusinessInsight:
        category_label = candidate.canonical_category.replace("_", " ")
        local = candidate.suburb or candidate.city
        return CandidateBusinessInsight(
            candidate_business_id=candidate.id,
            insight_run_id=insight_run_id,
            category=candidate.canonical_category,
            campaign_lane=campaign_lane,
            business_context_summary=f"{candidate.display_name} is a {category_label} candidate in {local}.",
            likely_customer_path="A customer likely wants to understand services and take a direct enquiry or booking action.",
            main_friction_points_json=["customer action path may be less direct without an owned website"],
            opportunity_summary="A lightweight owned web presence could make the next customer action easier to find.",
            confidence=0.75,
            evidence_json={"candidate_id": candidate.id, "campaign_lane": campaign_lane},
        )
