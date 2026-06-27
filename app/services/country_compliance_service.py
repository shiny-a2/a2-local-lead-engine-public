from pathlib import Path

import yaml

DEFAULT_PATH = Path("app/config/country_compliance.yaml")


class CountryComplianceService:
    """Per-country bulk/cold-email rules. Blocks sends to countries that require prior
    opt-in consent (most of the EU, Turkey, etc.) and reports each country's requirements.
    Conservative by default: unknown countries are blocked.
    """

    def __init__(self, path: Path | str = DEFAULT_PATH):
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        self._default: dict = data.get("default", {})
        self._countries: dict[str, dict] = data.get("countries", {})

    def known_countries(self) -> list[str]:
        return list(self._countries.keys())

    def rules(self, country: str | None) -> dict:
        if not country:
            return self._default
        return self._countries.get(country.strip(), self._default)

    def evaluate(self, country: str | None) -> dict:
        rule = self.rules(country)
        allowed = bool(rule.get("cold_b2b_allowed", False))
        return {
            "country": country or "unknown",
            "law": rule.get("law", "unknown"),
            "consent_model": rule.get("consent_model", "opt_in_required"),
            "cold_b2b_allowed": allowed,
            "requires_unsubscribe": rule.get("requires_unsubscribe", True),
            "requires_physical_address": rule.get("requires_physical_address", False),
            "honor_unsub_days": rule.get("honor_unsub_days", 10),
            "risk": rule.get("risk", "high"),
            "notes": rule.get("notes", ""),
            "allowed": allowed,
            "block_reason": None if allowed else f"{country or 'unknown'} requires prior opt-in consent ({rule.get('consent_model')})",
        }
