import re
from time import perf_counter

import httpx

from app.core.enums import UrlProbeStatus
from app.core.fingerprints import stable_fingerprint
from app.services.domain_classifier_service import domain_from_url
from app.settings import Settings


class UrlProbeService:
    def __init__(self, settings: Settings):
        self.settings = settings

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
            return {
                "url": url,
                "domain": domain,
                "final_url": str(response.url),
                "status_code": response.status_code,
                "is_redirect": str(response.url) != url,
                "redirect_chain_json": [str(item.url) for item in response.history],
                "title": title.group(1).strip()[:500] if title else None,
                "content_sample_hash": stable_fingerprint(sample),
                "probe_status": UrlProbeStatus.OK,
                "duration_ms": int((perf_counter() - start) * 1000),
            }
        except httpx.TimeoutException:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.TIMEOUT}
        except httpx.ConnectError as exc:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.DNS_ERROR, "error_message": str(exc)[:200]}
        except Exception as exc:
            return {"url": url, "domain": domain, "probe_status": UrlProbeStatus.FAILED, "error_message": str(exc)[:200]}

