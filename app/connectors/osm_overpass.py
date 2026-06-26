from typing import Any

import httpx

from app.connectors.base import BaseConnector, ConfigCheck, ConnectorRequest
from app.connectors.geoapify import _common_evidence
from app.core.enums import RawRecordType, SourceName


class OsmOverpassConnector(BaseConnector):
    source_name = SourceName.OSM_OVERPASS

    def check_config(self) -> ConfigCheck:
        return ConfigCheck(True, "AVAILABLE_NO_KEY_REQUIRED")

    def estimate_cost_or_credits(self, params: dict[str, Any]) -> int:
        return 1

    def build_request(self, params: dict[str, Any]) -> ConnectorRequest:
        tag_key = params["osm_tag_key"]
        tag_values = "|".join(params["osm_tag_values"])
        limit = int(params["limit"])
        city = params["city"]
        country = params.get("country", "")
        country_code = params.get("country_code", "")
        # Match the city by its local OSM name OR its English name (name:en), so non-English
        # cities like "Munich" (München) or "Tehran" (تهران) resolve the same way. Constrain
        # to the country so same-named cities elsewhere (e.g. Sydney AU vs Sydney CA) do not
        # bleed in. The ISO 3166-1 country code is the reliable area key (some country names,
        # e.g. New Zealand, have no usable name-based area); fall back to name/name:en.
        if country_code:
            country_clause = f'area["ISO3166-1"="{country_code}"]->.country;'
            country_filters = ("(area.country)",)
        elif country:
            country_clause = (
                f'area["name"="{country}"]->.country;'
                f'area["name:en"="{country}"]->.countryEn;'
            )
            country_filters = ("(area.country)", "(area.countryEn)")
        else:
            country_clause = ""
            country_filters = ("",)
        members = "".join(
            f'node["{tag_key}"~"{tag_values}"](area.{area}){cf};'
            f'way["{tag_key}"~"{tag_values}"](area.{area}){cf};'
            f'relation["{tag_key}"~"{tag_values}"](area.{area}){cf};'
            for area in ("searchArea", "searchAreaEn", "searchAreaPfx")
            for cf in country_filters
        )
        query = (
            f'[out:json][timeout:{self.settings.osm_timeout_seconds}];'
            f'area["name"="{city}"]["boundary"="administrative"]->.searchArea;'
            f'area["name:en"="{city}"]["boundary"="administrative"]->.searchAreaEn;'
            # Prefix match (e.g. "Hamilton City", "Auckland Council"); ($| ) avoids
            # grabbing "Bathgate" when the city is "Bath". Country filter keeps it in scope.
            f'area["name"~"^{city}($| )",i]["boundary"="administrative"]->.searchAreaPfx;'
            f"{country_clause}"
            f"({members});"
            f"out center {limit};"
        )
        key = f"osm:{params.get('country','')}:{city}:{params['category']}:{limit}"
        return ConnectorRequest("https://overpass-api.de/api/interpreter", {"data": query}, key)

    def extract_raw_records(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        records = []
        for item in response.get("elements", []):
            tags = item.get("tags", {})
            center = item.get("center", {})
            record_type = {
                "node": RawRecordType.OSM_NODE,
                "way": RawRecordType.OSM_WAY,
                "relation": RawRecordType.OSM_RELATION,
            }.get(item.get("type"), RawRecordType.OSM_NODE)
            website = tags.get("website") or tags.get("contact:website")
            phone = tags.get("phone") or tags.get("contact:phone")
            email = tags.get("email") or tags.get("contact:email")
            records.append(
                {
                    "source_name": self.source_name,
                    "source_external_id": str(item.get("id"))
                    if item.get("id") is not None
                    else None,
                    "record_type": record_type,
                    "raw_name": tags.get("name"),
                    "raw_category": tags.get("shop") or tags.get("craft") or tags.get("amenity"),
                    "raw_address": tags.get("addr:full") or tags.get("addr:street"),
                    "raw_city": tags.get("addr:city"),
                    "raw_suburb": tags.get("addr:suburb"),
                    "raw_country": tags.get("addr:country"),
                    "raw_lat": item.get("lat") or center.get("lat"),
                    "raw_lng": item.get("lon") or center.get("lon"),
                    "raw_phone": phone,
                    "raw_email": email,
                    "raw_website": website,
                    "raw_opening_hours_json": tags.get("opening_hours"),
                    "raw_social_links_json": {
                        key: value
                        for key, value in tags.items()
                        if "facebook" in key or "instagram" in key
                    },
                    "raw_payload_json": item,
                }
            )
        return records

    # Overpass mirrors tried in order; the public instance rejects requests without a
    # descriptive User-Agent (returns HTTP 406), so headers are mandatory.
    OVERPASS_ENDPOINTS = (
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    )

    def execute(self, request: ConnectorRequest, dry_run: bool) -> dict[str, Any]:
        if dry_run:
            return super().execute(request, dry_run=True)
        headers = {
            "User-Agent": "A2LocalLeadEngine/1.0 (amiraliyaghouti.com)",
            "Accept": "application/json",
        }
        endpoints = [request.url, *(e for e in self.OVERPASS_ENDPOINTS if e != request.url)]
        last_error: Exception | None = None
        for endpoint in endpoints:
            try:
                response = httpx.post(
                    endpoint,
                    data=request.params,
                    headers=headers,
                    timeout=self.settings.osm_timeout_seconds,
                )
                response.raise_for_status()
                return response.json()
            except Exception as exc:  # noqa: BLE001 - fall back to the next mirror
                last_error = exc
        raise last_error if last_error else RuntimeError("OSM Overpass request failed")

    def extract_personalization_evidence(self, raw_record: dict[str, Any]) -> list[dict[str, Any]]:
        return _common_evidence(raw_record, self.source_name.value)
