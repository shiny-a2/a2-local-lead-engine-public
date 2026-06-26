from app.core.enums import PricePositioning, PriceVisibility
from app.db.models.price_positioning_recommendation import PricePositioningRecommendation


class PricePositioningService:
    def build(self, candidate_id: int, insight_run_id: int) -> PricePositioningRecommendation:
        return PricePositioningRecommendation(
            candidate_business_id=candidate_id,
            insight_run_id=insight_run_id,
            price_positioning=PricePositioning.MODULAR_LOW_RISK_START,
            price_visibility=PriceVisibility.MENTION_LATER,
            price_risk="avoid exact first-email quote",
            recommended_language_json=["lightweight starter version", "simple first version"],
            blocked_language_json=["cheap website", "$99 guaranteed", "final quote"],
        )
