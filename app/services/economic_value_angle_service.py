from app.core.enums import ClaimStrength, EconomicAngleType, OfferPackage
from app.db.models.blocked_offer_claim import BlockedOfferClaim
from app.db.models.candidate_economic_value_angle import CandidateEconomicValueAngle
from app.services.offer_risk_service import OfferRiskService


class EconomicValueAngleService:
    safe_by_package = {
        OfferPackage.BOOKING_SYSTEM_SITE: (
            EconomicAngleType.DIRECT_BOOKING_PATH,
            "help customers book or enquire directly through your own website",
        ),
        OfferPackage.LOCAL_TRUST_SITE: (
            EconomicAngleType.LOWER_FRICTION_CUSTOMER_ACTION,
            "make services, prices, and contact options easier to find",
        ),
        OfferPackage.QUOTE_REQUEST_SITE: (
            EconomicAngleType.DIRECT_QUOTE_REQUESTS,
            "create a clearer path for direct quote requests",
        ),
        OfferPackage.MENU_QR_SITE: (
            EconomicAngleType.DIRECT_MENU_OWNERSHIP,
            "keep menu information on an owned, easy-to-update page",
        ),
    }

    risky_claims = [
        "guaranteed more bookings",
        "stop paying commissions",
        "save thousands",
        "replace all third-party platforms",
        "you are losing customers",
    ]

    def build(self, candidate_id: int, insight_run_id: int, package: OfferPackage) -> tuple[list[CandidateEconomicValueAngle], list[BlockedOfferClaim]]:
        angle_type, text = self.safe_by_package.get(
            package,
            (EconomicAngleType.MODULAR_UPGRADE_PATH, "start with a lightweight version and upgrade later"),
        )
        angles = [
            CandidateEconomicValueAngle(
                candidate_business_id=candidate_id,
                insight_run_id=insight_run_id,
                angle_type=angle_type,
                angle_text=text,
                claim_strength=ClaimStrength.CAUTIOUS,
                allowed_for_future_copy=True,
                requires_verification=False,
                evidence_json={"offer_package": package.value},
            ),
            CandidateEconomicValueAngle(
                candidate_business_id=candidate_id,
                insight_run_id=insight_run_id,
                angle_type=EconomicAngleType.MODULAR_UPGRADE_PATH,
                angle_text="start with a lightweight version and upgrade later",
                claim_strength=ClaimStrength.SAFE_GENERAL,
                allowed_for_future_copy=True,
                requires_verification=False,
                evidence_json={"offer_package": package.value},
            ),
        ]
        blocked = [
            BlockedOfferClaim(
                candidate_business_id=candidate_id,
                insight_run_id=insight_run_id,
                claim_text=claim,
                reason=OfferRiskService().blocked_reason(claim) or "unsupported economic claim",
                severity="BLOCKER",
            )
            for claim in self.risky_claims
        ]
        return angles, blocked
