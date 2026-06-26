from app.core.enums import DomainClassification
from app.db.models.candidate_business import CandidateBusiness
from app.services.domain_classifier_service import DomainClassifierService, domain_from_url


class WebsiteOwnershipService:
    def confidence(self, candidate: CandidateBusiness, result: dict) -> tuple[float, list[str], list[str]]:
        reasons: list[str] = []
        risks: list[str] = []
        url = result.get("url", "")
        domain_class = DomainClassifierService().classify(url, candidate.display_name)
        if domain_class in {DomainClassification.SOCIAL_DOMAIN, DomainClassification.DIRECTORY_DOMAIN}:
            return 0.0, [], ["social_or_directory_not_official"]
        score = 20.0
        text = f"{result.get('title', '')} {result.get('snippet', '')} {domain_from_url(url)}".lower()
        for token in candidate.display_name.lower().split():
            if len(token) > 2 and token in text:
                score += 15
                reasons.append("business_name_signal")
                break
        if candidate.city and candidate.city.lower() in text:
            score += 15
            reasons.append("city_signal")
        if candidate.canonical_category and candidate.canonical_category.replace("_", " ") in text:
            score += 10
            reasons.append("category_signal")
        if "parked" in text or "for sale" in text:
            score -= 40
            risks.append("parked_or_broken")
        if score < 50:
            risks.append("unclear_ownership")
        return max(0, min(100, score)), reasons, risks
