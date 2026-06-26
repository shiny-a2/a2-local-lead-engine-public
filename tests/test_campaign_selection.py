from app.core.enums import CampaignFitStatus, CampaignLane, Phase4WebsiteStatus
from app.services.campaign_selection_service import CampaignSelectionService


def test_no_website_confirmed_goes_to_no_website_lane():
    fit = CampaignSelectionService().assess(Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED, "barber")
    assert fit.lane == CampaignLane.NO_WEBSITE


def test_social_and_directory_lanes():
    service = CampaignSelectionService()
    assert service.assess(Phase4WebsiteStatus.SOCIAL_ONLY, "barber").lane == CampaignLane.SOCIAL_ONLY
    assert service.assess(Phase4WebsiteStatus.DIRECTORY_ONLY, "barber").lane == CampaignLane.DIRECTORY_ONLY


def test_weak_and_strong_website_hold_or_reject():
    service = CampaignSelectionService()
    assert service.assess(Phase4WebsiteStatus.WEAK_WEBSITE_FOUND, "barber").status == CampaignFitStatus.HOLD
    assert service.assess(Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL, "barber").status == CampaignFitStatus.NOT_FIT
