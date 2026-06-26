from typing import Any

import httpx

from app.connectors.base import BaseConnector, ConfigCheck, ConnectorRequest
from app.core.enums import RawRecordType, SourceName


class GeoapifyPlacesConnector(BaseConnector):
    source_name = SourceName.GEOAPIFY

    def check_config(self) -> ConfigCheck:
        if not self.settings.geoapify_api_key:
            return ConfigCheck(False, "GEOAPIFY_API_KEY_MISSING")
        return ConfigCheck(True, "CONFIGURED")

    def estimate_cost_or_credits(self, params: dict[str, Any]) -> int:
        return max(1, int(params.get("request_count", 1)))

    def build_request(self, params: dict[str, Any]) -> ConnectorRequest:
        request_params = {
            "categories": params["source_category"],
            "filter": f"place:{params['city']},{params['country']}",
            "limit": params["limit"],
            "apiKey": "***REDACTED***",
        }
        key = (
            f"geoapify:{params['country']}:{params['city']}:"
            f"{params['category']}:{params['limit']}"
        )
        return ConnectorRequest("https://api.geoapify.com/v2/places", request_params, key)

    def execute(self, request: ConnectorRequest, dry_run: bool) -> dict[str, Any]:
        if dry_run:
            return super().execute(request, dry_run=True)
        params = {**request.params, "apiKey": self.settings.geoapify_api_key}
        response = httpx.get(request.url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def extract_raw_records(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        records = []
        for feature in response.get("features", []):
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coords = geometry.get("coordinates") or [None, None]
            records.append(
                {
                    "source_name": self.source_name,
                    "source_external_id": props.get("place_id")
                    or props.get("datasource", {}).get("raw", {}).get("osm_id"),
                    "record_type": RawRecordType.PLACE,
                    "raw_name": props.get("name"),
                    "raw_category": props.get("categories", [None])[0]
                    if isinstance(props.get("categories"), list)
                    else props.get("categories"),
                    "raw_address": props.get("formatted"),
                    "raw_city": props.get("city"),
                    "raw_suburb": props.get("suburb") or props.get("district"),
                    "raw_country": props.get("country"),
                    "raw_lat": coords[1],
                    "raw_lng": coords[0],
                    "raw_phone": props.get("contact", {}).get("phone"),
                    "raw_email": props.get("contact", {}).get("email"),
                    "raw_website": props.get("website") or props.get("contact", {}).get("website"),
                    "raw_opening_hours_json": props.get("opening_hours"),
                    "raw_social_links_json": props.get("social"),
                    "raw_payload_json": feature,
                }
            )
        return records

    def extract_personalization_evidence(self, raw_record: dict[str, Any]) -> list[dict[str, Any]]:
        return _common_evidence(raw_record, self.source_name.value)


def _common_evidence(raw_record: dict[str, Any], source: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    def add(kind: str, value: object, allowed: bool, verify: bool, risk: str | None = None) -> None:
        if value not in (None, "", []):
            items.append(
                {
                    "evidence_type": kind,
                    "evidence_value": str(value),
                    "evidence_source": source,
                    "confidence": 0.7,
                    "allowed_for_future_copy": allowed,
                    "requires_verification": verify,
                    "risk_flag": risk,
                }
            )

    add("business_name", raw_record.get("raw_name"), True, True)
    add("category_hint", raw_record.get("raw_category"), True, True)
    add("suburb_hint", raw_record.get("raw_suburb"), True, True)
    add("local_area_hint", raw_record.get("raw_city"), True, True)
    if raw_record.get("raw_website"):
        add("website_field_present", raw_record.get("raw_website"), False, True)
    else:
        add("website_field_missing", "missing_in_raw_source", False, True)
    add(
        "phone_present",
        raw_record.get("raw_phone"),
        False,
        True,
        "contact_data_not_outreach_permission",
    )
    add("email_present_raw", raw_record.get("raw_email"), False, True, "not_outreach_permission")
    add("opening_hours_present", raw_record.get("raw_opening_hours_json"), True, True)
    add("service_category_hint", raw_record.get("raw_category"), True, True)
    return items
