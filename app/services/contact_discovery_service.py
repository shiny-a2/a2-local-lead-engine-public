import re

import httpx

from app.core.enums import SensitiveOperation
from app.core.safety import check_operation
from app.services.contact_relevance_service import ContactRelevanceService
from app.settings import Settings

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")
# noise / non-contact addresses that show up on pages and directories
SKIP_TOKENS = (
    "example.", "sentry", "wixpress", "godaddy", "squarespace", "@sentry", "yourdomain",
    "domain.com", ".png", ".jpg", ".webp", "u003", "core.noreply", "no-reply@",
)


class ContactDiscoveryService:
    """Find a business's public contact email via the Tavily search API (free tier).

    Returns raw candidates only; relevance to the specific business and legal
    eligibility are decided downstream (relevance agent + contact risk + compliance).
    """

    def __init__(self, settings: Settings, http_post=None):
        self.settings = settings
        self._post = http_post or self._default_post

    def _default_post(self, payload: dict):
        return httpx.post("https://api.tavily.com/search", json=payload, timeout=30)

    def can_run(self) -> tuple[bool, str]:
        if not self.settings.contact_discovery_enabled:
            return False, "CONTACT_DISCOVERY_DISABLED"
        if not self.settings.tavily_api_key:
            return False, "TAVILY_API_KEY_MISSING"
        if not check_operation(self.settings, SensitiveOperation.LIVE_API_CALL).allowed:
            return False, "LIVE_API_CALLS_DISABLED"
        return True, "ALLOWED"

    def search_emails(self, business_name: str, city: str | None, category: str | None = None, country: str | None = None) -> list[dict]:
        ok, _reason = self.can_run()
        if not ok or not business_name:
            return []
        relevance = ContactRelevanceService()
        query = " ".join(
            part for part in [business_name, city or "", (category or "").replace("_", " "), "contact email"] if part
        )
        payload = {
            "api_key": self.settings.tavily_api_key,
            "query": query,
            "max_results": self.settings.contact_discovery_max_results,
            "include_answer": False,
        }
        try:
            response = self._post(payload)
            response.raise_for_status()
            results = response.json().get("results", [])
        except Exception:
            return []
        found: list[dict] = []
        seen: set[str] = set()
        for res in results:
            url = res.get("url", "")
            blob = f"{res.get('title', '')} {res.get('content', '')}"
            for email in EMAIL_RE.findall(blob):
                email = email.strip().rstrip(".")
                low = email.lower()
                if low in seen or any(tok in low for tok in SKIP_TOKENS):
                    continue
                seen.add(low)
                # Drop emails that belong to a different / directory business.
                if not relevance.is_plausible(business_name, country, email)[0]:
                    continue
                found.append(
                    {
                        "email": email,
                        "source_url": url,
                        "title": res.get("title", ""),
                        "snippet": res.get("content", "")[:200],
                    }
                )
        return found

    def discovery_results(self, business_name: str, city: str | None, category: str | None = None, country: str | None = None) -> list[dict]:
        """Result dicts shaped for ContactExtractionService (title / url / snippet)."""
        return [
            {
                "title": item["title"] or business_name,
                "url": item["source_url"],
                "snippet": f"{business_name} {city or ''} {item['email']}",
            }
            for item in self.search_emails(business_name, city, category, country)
        ]
