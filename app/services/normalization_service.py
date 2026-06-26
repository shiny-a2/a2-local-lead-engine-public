import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

GENERIC_NAMES = {
    "the barber",
    "barber shop",
    "hair studio",
    "beauty salon",
    "cleaning services",
    "auckland cleaning",
}
LEGAL_SUFFIXES = {"ltd", "limited", "llc", "inc", "company", "co"}


@dataclass(frozen=True)
class NormalizedName:
    display_name: str
    canonical_name: str
    normalized_name: str
    generic_risk_score: float


class NormalizationService:
    def normalize_name(self, raw_name: str | None) -> NormalizedName:
        display = " ".join((raw_name or "").strip().split())
        canonical = display
        normalized = display.lower().replace("’", "'").replace("`", "'")
        normalized = normalized.replace("&", " and ")
        normalized = re.sub(r"[^a-z0-9\s']", " ", normalized)
        parts = [part for part in normalized.split() if part not in LEGAL_SUFFIXES]
        normalized = " ".join(parts)
        generic = 80.0 if normalized in GENERIC_NAMES else 0.0
        if not normalized or normalized in {"barber", "cleaner", "beauty"}:
            generic = 90.0
        return NormalizedName(canonical, canonical, normalized, generic)

    def canonicalize_category(
        self, raw_category: str | None, source_name: str | None = None
    ) -> str | None:
        if not raw_category:
            return None
        needle = raw_category.lower()
        mapping = yaml.safe_load(Path("app/config/source_category_map.yaml").read_text())
        for internal, source_map in mapping.items():
            geo = source_map.get("geoapify", {}).get("categories", [])
            if needle in [item.lower() for item in geo]:
                return internal
            for values in source_map.get("osm", {}).get("tags", {}).values():
                if needle in [item.lower() for item in values]:
                    return internal
        if needle in mapping:
            return needle
        return None

    def normalize_address(self, raw_address: str | None) -> str | None:
        return " ".join(raw_address.split()) if raw_address else None

    def geo_hash(self, lat: float | None, lng: float | None, precision: int = 3) -> str | None:
        if lat is None or lng is None:
            return None
        return f"{round(lat, precision)}:{round(lng, precision)}"

    def identity_fingerprint(self, values: dict[str, Any]) -> str:
        from app.core.fingerprints import stable_fingerprint

        return stable_fingerprint(
            {
                "normalized_name": values.get("normalized_name"),
                "canonical_category": values.get("canonical_category"),
                "city": (values.get("city") or "").lower(),
                "suburb_or_geo": (values.get("suburb") or values.get("geo_hash") or "").lower(),
            }
        )
