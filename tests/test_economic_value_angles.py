from app.core.enums import OfferPackage
from app.services.economic_value_angle_service import EconomicValueAngleService
from app.services.offer_risk_service import OfferRiskService


def test_safe_economic_angles_created():
    angles, blocked = EconomicValueAngleService().build(1, 1, OfferPackage.QUOTE_REQUEST_SITE)
    assert any("direct quote" in angle.angle_text for angle in angles)
    assert all(angle.allowed_for_future_copy for angle in angles)
    assert blocked


def test_aggressive_claims_blocked():
    risk = OfferRiskService()
    assert risk.blocked_reason("guaranteed more bookings")
    assert risk.blocked_reason("stop paying commissions")
    assert risk.blocked_reason("replace all third-party platforms")
