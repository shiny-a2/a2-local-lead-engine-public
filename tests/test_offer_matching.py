from app.core.enums import CampaignLane, OfferPackage
from app.services.offer_matching_service import OfferMatchingService


def test_category_offer_packages():
    service = OfferMatchingService()
    assert service.package_for("beauty_salon", CampaignLane.NO_WEBSITE) == OfferPackage.BOOKING_SYSTEM_SITE
    assert service.package_for("barber", CampaignLane.NO_WEBSITE) == OfferPackage.LOCAL_TRUST_SITE
    assert service.package_for("cleaning_service", CampaignLane.NO_WEBSITE) == OfferPackage.QUOTE_REQUEST_SITE
    assert service.package_for("cafe", CampaignLane.NO_WEBSITE) == OfferPackage.MENU_QR_SITE
    assert service.package_for("barber", CampaignLane.WEAK_WEBSITE) == OfferPackage.WEAK_WEBSITE_REFRESH
