from urllib.parse import urlparse

from app.core.enums import DomainClassification

SOCIAL_DOMAINS = ("facebook.com", "instagram.com", "linkedin.com", "tiktok.com", "x.com", "youtube.com")
DIRECTORY_DOMAINS = ("yellow.co.nz", "finda.co.nz", "localist.co.nz", "yelp", "tripadvisor", "foursquare", "cylex", "hotfrog")
BOOKING_DOMAINS = ("fresha.com", "booksy.com", "setmore.com", "calendly.com")
MARKETPLACE_DOMAINS = ("trademe.co.nz", "marketplace")
PARKED_TERMS = ("parked", "domain-for-sale", "sedo")


def domain_from_url(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    return parsed.netloc.lower().removeprefix("www.")


class DomainClassifierService:
    def classify(self, url_or_domain: str, candidate_name: str | None = None) -> DomainClassification:
        domain = domain_from_url(url_or_domain)
        if any(item in domain for item in SOCIAL_DOMAINS):
            return DomainClassification.SOCIAL_DOMAIN
        if any(item in domain for item in DIRECTORY_DOMAINS):
            return DomainClassification.DIRECTORY_DOMAIN
        if any(item in domain for item in BOOKING_DOMAINS):
            return DomainClassification.BOOKING_PLATFORM_DOMAIN
        if any(item in domain for item in MARKETPLACE_DOMAINS):
            return DomainClassification.MARKETPLACE_DOMAIN
        if any(item in domain for item in PARKED_TERMS):
            return DomainClassification.PARKED_DOMAIN
        if candidate_name:
            tokens = [token for token in candidate_name.lower().split() if len(token) > 2]
            if tokens and any(token in domain for token in tokens):
                return DomainClassification.OFFICIAL_CANDIDATE_DOMAIN
        if domain.endswith((".zip", ".mov")):
            return DomainClassification.SUSPICIOUS_DOMAIN
        return DomainClassification.UNKNOWN_DOMAIN

