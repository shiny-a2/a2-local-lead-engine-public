from app.core.enums import DomainClassification, SearchResultType
from app.db.models.candidate_business import CandidateBusiness
from app.services.domain_classifier_service import DomainClassifierService


class SearchResultClassifier:
    def __init__(self):
        self.domains = DomainClassifierService()

    def classify(self, result: dict, candidate: CandidateBusiness) -> tuple[SearchResultType, DomainClassification]:
        url = result.get("url", "")
        domain_class = self.domains.classify(url, candidate.display_name)
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        if domain_class == DomainClassification.SOCIAL_DOMAIN:
            return SearchResultType.SOCIAL_PROFILE, domain_class
        if domain_class == DomainClassification.DIRECTORY_DOMAIN:
            return SearchResultType.DIRECTORY_LISTING, domain_class
        if domain_class == DomainClassification.BOOKING_PLATFORM_DOMAIN:
            return SearchResultType.BOOKING_PAGE, domain_class
        if domain_class == DomainClassification.MARKETPLACE_DOMAIN:
            return SearchResultType.MARKETPLACE_PAGE, domain_class
        if domain_class == DomainClassification.OFFICIAL_CANDIDATE_DOMAIN:
            return SearchResultType.POSSIBLE_OFFICIAL_WEBSITE, domain_class
        if candidate.display_name.lower() in text and candidate.city.lower() in text:
            return SearchResultType.POSSIBLE_OFFICIAL_WEBSITE, domain_class
        if "unrelated" in text:
            return SearchResultType.IRRELEVANT, domain_class
        return SearchResultType.UNKNOWN, domain_class
