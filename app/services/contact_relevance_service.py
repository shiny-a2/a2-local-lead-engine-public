import re

# TLDs that strongly imply a different country than a New Zealand / AU / generic business.
FOREIGN_TLDS = {
    "dk", "de", "fr", "se", "no", "fi", "nl", "es", "it", "ru", "cn", "in", "br", "pl",
    "cz", "gr", "pt", "ro", "tr", "jp", "kr", "mx", "ar", "za", "ch", "at", "be",
}
# Aggregator / directory / generic domains that are never a specific business's own contact.
DIRECTORY_HINTS = (
    "findmylocal", "yellow", "finda", "localist", "yelp", "tripadvisor", "cylex", "hotfrog",
    "nzbusiness", "businessdirectory", "beautysalon", "beautycare", "hairdresser", "directory",
    "google", "facebook", "instagram",
)


def _domain_main(domain: str) -> str:
    return domain.split(".")[0]


class ContactRelevanceService:
    """Cheap, keyless check that a discovered contact email plausibly belongs to THIS business.

    Tavily/web search often returns the email of a same-named business in another country, or a
    directory/aggregator address. Those must not be emailed. Heuristics:
      - the email-domain stem must share a meaningful token with the business name, OR be a
        role address on a domain that does; AND
      - it must not be a known directory/aggregator domain; AND
      - for an NZ business, the TLD must not be a clearly-foreign country code.
    """

    def is_plausible(self, business_name: str, country: str | None, email: str) -> tuple[bool, str]:
        if not email or "@" not in email:
            return False, "no email"
        local, _, domain = email.lower().partition("@")
        domain = domain.strip()
        stem = _domain_main(domain)
        tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
        name_tokens = [t for t in re.findall(r"[a-z]+", business_name.lower()) if len(t) > 2]

        if any(hint in domain for hint in DIRECTORY_HINTS):
            return False, "email is on a directory/aggregator domain, not the business's own"

        overlap = any(t in stem or (len(stem) > 2 and stem in t) for t in name_tokens)
        if not overlap:
            return False, "email domain does not match the business name"

        if tld in FOREIGN_TLDS and country and "new zealand" in country.lower():
            return False, f"email is on a foreign domain (.{tld}) for a New Zealand business"

        return True, "plausible match"

    def filter_emails(self, business_name: str, country: str | None, emails: list[str]) -> list[str]:
        return [e for e in emails if self.is_plausible(business_name, country, e)[0]]
