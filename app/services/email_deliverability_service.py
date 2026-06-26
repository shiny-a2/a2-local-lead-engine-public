import httpx


class EmailDeliverabilityService:
    """Free, keyless deliverability check for a sending domain.

    Uses public DNS-over-HTTPS (Google) to look up SPF / DMARC / DKIM TXT records.
    No API key, no signup, no credit card. Helps decide whether a domain is safe to
    cold-email from before any send is enabled.
    """

    DOH_URL = "https://dns.google/resolve"
    COMMON_DKIM_SELECTORS = (
        "default", "mail", "dkim", "selector1", "selector2", "google", "k1", "s1", "smtp",
    )

    def __init__(self, http_get=None):
        self._http_get = http_get or self._doh_get

    def _doh_get(self, name: str, record_type: str = "TXT") -> list[str]:
        try:
            response = httpx.get(
                self.DOH_URL,
                params={"name": name, "type": record_type},
                headers={"Accept": "application/dns-json"},
                timeout=10,
            )
            if response.status_code != 200:
                return []
            answers = response.json().get("Answer", []) or []
            return [str(a.get("data", "")).strip().strip('"') for a in answers]
        except Exception:
            return []

    def check_domain(self, domain: str) -> dict:
        domain = domain.strip().lower().lstrip("@")
        spf = [t for t in self._http_get(domain) if "v=spf1" in t.lower()]
        dmarc = [t for t in self._http_get(f"_dmarc.{domain}") if "v=dmarc1" in t.lower()]
        dkim_selectors = []
        for selector in self.COMMON_DKIM_SELECTORS:
            records = self._http_get(f"{selector}._domainkey.{domain}")
            if any("dkim1" in r.lower() or "p=" in r for r in records):
                dkim_selectors.append(selector)
        return {
            "domain": domain,
            "spf": "present" if spf else "MISSING",
            "spf_record": spf[0] if spf else None,
            "dmarc": "present" if dmarc else "MISSING",
            "dmarc_record": dmarc[0] if dmarc else None,
            "dkim_selectors_found": dkim_selectors or "none_found_in_common_selectors",
            "ready_for_cold_email": bool(spf and dmarc),
            "note": "DKIM uses a custom selector; 'none_found' just means it is not one of "
            "the common names. Confirm your selector in cPanel > Email Deliverability.",
        }
