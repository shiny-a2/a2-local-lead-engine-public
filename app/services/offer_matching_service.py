from app.core.enums import CampaignLane, OfferPackage
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_offer_match import CandidateOfferMatch
from app.db.models.offer_module import OfferModule
from app.db.models.offer_playbook import OfferPlaybook


class OfferMatchingService:
    def package_for(self, category: str, lane: CampaignLane) -> OfferPackage:
        if lane == CampaignLane.WEAK_WEBSITE:
            return OfferPackage.WEAK_WEBSITE_REFRESH
        if lane == CampaignLane.SOCIAL_ONLY:
            return OfferPackage.SOCIAL_TO_OWNED_SITE
        if category == "beauty_salon":
            return OfferPackage.BOOKING_SYSTEM_SITE
        if category == "barber":
            return OfferPackage.LOCAL_TRUST_SITE
        if category == "cleaning_service":
            return OfferPackage.QUOTE_REQUEST_SITE
        if category == "cafe":
            return OfferPackage.MENU_QR_SITE
        return OfferPackage.STARTER_DIRECT_SITE

    def build(
        self,
        candidate: CandidateBusiness,
        insight_run_id: int,
        playbook: OfferPlaybook,
        lane: CampaignLane,
        selected: list[OfferModule],
        excluded: list[OfferModule],
    ) -> CandidateOfferMatch:
        package = self.package_for(candidate.canonical_category, lane)
        score = 88.0 if candidate.canonical_category in {"beauty_salon", "barber", "cleaning_service"} else 55.0
        return CandidateOfferMatch(
            candidate_business_id=candidate.id,
            insight_run_id=insight_run_id,
            playbook_id=playbook.id,
            offer_package=package,
            offer_fit_score=score,
            offer_confidence=0.8,
            offer_summary=f"{package.value} matched from {playbook.playbook_name}.",
            internal_offer_analysis="Rule-based category and lane match; no AI or external data used.",
            email_safe_offer_summary="A lightweight owned web presence focused on a clearer customer action path.",
            primary_value_angle="direct customer action path",
            secondary_value_angles_json=["owned brand presence", "modular upgrade path"],
            selected_module_ids_json=[module.id for module in selected],
            excluded_module_ids_json=[module.id for module in excluded],
        )
