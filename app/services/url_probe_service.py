import re
from time import perf_counter

import httpx

from app.core.enums import UrlProbeStatus
from app.core.fingerprints import stable_fingerprint
from app.services.domain_classifier_service import domain_from_url
from app.settings import Settings

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_EMAIL_SKIP = ("noreply", "no-reply", "donotreply", "example.com", "sentry", "wixpress", "wix.com", "godaddy", "squarespace", ".png", ".jpg", ".gif", ".webp")


def _strip_www(domain: str | None) -> str:
    return (domain or "").lower().removeprefix("www.")


class UrlProbeService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def scrape_same_domain_emails(self, html: str, final_url: str) -> list[str]:
        """Emails published on the business's OWN homepage (same registrable domain only). The
        same-domain filter is the wrong-business safeguard: third-party/widget addresses are dropped."""
        self_domain = _strip_www(domain_from_url(final_url))
        if not self_domain:
            return []
        found = re.findall(r"mailto:([^\"'?>\s]+)", html, re.I)
        found.extend(_EMAIL_RE.findall(html))
        out: list[str] = []
        for raw in dict.fromkeys(x.strip().lower() for x in found):
            if "@" not in raw or any(tok in raw for tok in _EMAIL_SKIP):
                continue
            if _strip_www(raw.split("@")[-1]) == self_domain:
                out.append(raw)
        return out[:5]

    def probe(self, url: str, dry_run: bool = True) -> dict:
        domain = domain_from_url(url)
        if dry_run:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.SKIPPED_DRY_RUN}
        if not self.settings.url_probe_enabled:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.SKIPPED_BY_POLICY}
        start = perf_counter()
        try:
            headers = {"User-Agent": self.settings.url_probe_user_agent}
            head = httpx.head(url, timeout=self.settings.url_probe_timeout_seconds, headers=headers, follow_redirects=True)
            content_type = head.headers.get("content-type", "")
            if "html" not in content_type and head.status_code < 400:
                return {"url": url, "domain": domain, "status_code": head.status_code, "probe_status": UrlProbeStatus.NON_HTML}
            response = httpx.get(url, timeout=self.settings.url_probe_timeout_seconds, headers=headers, follow_redirects=True)
            sample = response.text[: self.settings.url_probe_max_bytes]
            title = re.search(r"<title>(.*?)</title>", sample, re.I | re.S)
            final_url = str(response.url)
            return {
                "url": url,
                "domain": domain,
                "final_url": final_url,
                "status_code": response.status_code,
                "is_redirect": final_url != url,
                "redirect_chain_json": [str(item.url) for item in response.history],
                "title": title.group(1).strip()[:500] if title else None,
                "content_sample_hash": stable_fingerprint(sample),
                "scraped_emails": self.scrape_same_domain_emails(sample, final_url),
                "probe_status": UrlProbeStatus.OK,
                "duration_ms": int((perf_counter() - start) * 1000),
            }
        except httpx.TimeoutException:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.TIMEOUT}
        except httpx.ConnectError as exc:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.DNS_ERROR, "error_message": str(exc)[:200]}
        except Exception as exc:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.FAILED, "error_message": str(exc)[:200]}

