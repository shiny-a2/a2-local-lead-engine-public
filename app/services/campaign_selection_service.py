from dataclasses import dataclass

from app.core.enums import CampaignFitStatus, CampaignLane, Phase4WebsiteStatus


@dataclass(frozen=True)
class CampaignFit:
    lane: CampaignLane
    score: float
    status: CampaignFitStatus
    reason: str


class CampaignSelectionService:
    def assess(self, website_status: Phase4WebsiteStatus, category: str) -> CampaignFit:
        if category not in {"barber", "beauty_salon", "cleaning_service"}:
            return CampaignFit(CampaignLane.OUT_OF_SCOPE, 0, CampaignFitStatus.NOT_FIT, "category outside MVP scope")
        if website_status in {Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED, Phase4WebsiteStatus.NO_WEBSITE_PROBABLE}:
            return CampaignFit(CampaignLane.NO_WEBSITE, 95, CampaignFitStatus.FIT, "verified no dedicated website opportunity")
        if website_status == Phase4WebsiteStatus.SOCIAL_ONLY:
            return CampaignFit(CampaignLane.SOCIAL_ONLY, 88, CampaignFitStatus.FIT, "social-only web presence")
        if website_status == Phase4WebsiteStatus.DIRECTORY_ONLY:
            return CampaignFit(CampaignLane.DIRECTORY_ONLY, 82, CampaignFitStatus.FIT_WITH_WARNINGS, "directory-only web presence")
        if website_status == Phase4WebsiteStatus.WEAK_WEBSITE_FOUND:
            return CampaignFit(CampaignLane.WEAK_WEBSITE, 55, CampaignFitStatus.HOLD, "weak website belongs to a future campaign lane")
        if website_status == Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL:
            return CampaignFit(CampaignLane.FUTURE_CAMPAIGN, 0, CampaignFitStatus.NOT_FIT, "strong official website is not MVP no-website fit")
        return CampaignFit(CampaignLane.FUTURE_CAMPAIGN, 25, CampaignFitStatus.MANUAL_REVIEW, "web presence is unclear")
