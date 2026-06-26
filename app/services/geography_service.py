from pathlib import Path

import yaml

DEFAULT_PATH = Path("app/config/geography.yaml")


class GeographyService:
    """Loads the country -> big/small city registry used to target lead collection."""

    def __init__(self, path: Path | str = DEFAULT_PATH):
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        self._countries: dict[str, dict] = data.get("countries", {})

    def countries(self) -> list[str]:
        return list(self._countries.keys())

    def country(self, name: str) -> dict | None:
        return self._countries.get(name)

    def timezone(self, country: str) -> str | None:
        info = self._countries.get(country) or {}
        return info.get("timezone")

    def cities(self, country: str, size: str = "all") -> list[str]:
        info = self._countries.get(country)
        if not info:
            return []
        if size == "big":
            return list(info.get("big", []))
        if size == "small":
            return list(info.get("small", []))
        return list(info.get("big", [])) + list(info.get("small", []))

    def all_targets(self, size: str = "all") -> list[tuple[str, str]]:
        """Return (country, city) pairs across the whole registry."""
        return [
            (country, city)
            for country in self._countries
            for city in self.cities(country, size)
        ]

    def total_cities(self, size: str = "all") -> int:
        return sum(len(self.cities(country, size)) for country in self._countries)
