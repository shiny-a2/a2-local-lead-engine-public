from app.core.enums import ComplexityLevel, FeasibilityLevel
from app.db.models.implementation_feasibility_note import ImplementationFeasibilityNote
from app.db.models.offer_module import OfferModule


class ImplementationFeasibilityService:
    def note(self, candidate_id: int, insight_run_id: int, module: OfferModule) -> ImplementationFeasibilityNote:
        level = FeasibilityLevel.EASY
        if module.implementation_complexity == ComplexityLevel.MEDIUM:
            level = FeasibilityLevel.MODERATE
        if module.implementation_complexity == ComplexityLevel.HIGH:
            level = FeasibilityLevel.NOT_RECOMMENDED_FOR_FIRST_OFFER
        return ImplementationFeasibilityNote(
            candidate_business_id=candidate_id,
            insight_run_id=insight_run_id,
            module_slug=module.module_slug,
            feasibility_level=level,
            implementation_note="Suitable for a conservative first offer." if level != FeasibilityLevel.NOT_RECOMMENDED_FOR_FIRST_OFFER else "Keep out of the first offer.",
            risk_level=module.maintenance_risk,
        )
