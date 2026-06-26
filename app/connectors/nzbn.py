from typing import Any

import httpx

from app.connectors.base import BaseConnector, ConfigCheck, ConnectorRequest
from app.core.enums import SourceName


class NzbnConnector(BaseConnector):
    source_name = SourceName.NZBN

    def check_config(self) -> ConfigCheck:
        if not self.settings.nzbn_api_key:
            return ConfigCheck(False, "NZBN_API_KEY_MISSING")
        return ConfigCheck(True, "CONFIGURED")

    def estimate_cost_or_credits(self, params: dict[str, Any]) -> int:
        return max(1, int(params.get("request_count", 1)))

    def build_request(self, params: dict[str, Any]) -> ConnectorRequest:
        query = params["query_name"]
        return ConnectorRequest(
            "https://api.business.govt.nz/services/v4/nzbn/entities",
            {"search-term": query, "subscription-key": "***REDACTED***"},
            f"nzbn:{query.lower()}",
        )

    def execute(self, request: ConnectorRequest, dry_run: bool) -> dict[str, Any]:
        if dry_run:
            return super().execute(request, dry_run=True)
        params = {
            key: value
            for key, value in request.params.items()
            if key != "subscription-key"
        }
        headers = {"Ocp-Apim-Subscription-Key": self.settings.nzbn_api_key}
        response = httpx.get(request.url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def extract_raw_records(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        return []

    def extract_candidate_matches(
        self, response: dict[str, Any], query_name: str
    ) -> list[dict[str, Any]]:
        matches = []
        for item in response.get("items", response.get("entities", [])):
            name = item.get("entityName") or item.get("entity_name")
            score = item.get("score")
            matches.append(
                {
                    "query_name": query_name,
                    "nzbn": item.get("nzbn"),
                    "entity_name": name,
                    "entity_status": item.get("entityStatus") or item.get("entity_status"),
                    "entity_type": item.get("entityType") or item.get("entity_type"),
                    "score": score,
                    "match_confidence": score if isinstance(score, int | float) else None,
                    "raw_payload_json": item,
                }
            )
        return matches

    def extract_personalization_evidence(self, raw_record: dict[str, Any]) -> list[dict[str, Any]]:
        name = raw_record.get("entity_name") or raw_record.get("query_name")
        return [
            {
                "evidence_type": "business_name",
                "evidence_value": str(name),
                "evidence_source": self.source_name.value,
                "confidence": 0.6,
                "allowed_for_future_copy": True,
                "requires_verification": True,
                "risk_flag": None,
            },
            {
                "evidence_type": "source_quality_hint",
                "evidence_value": "nzbn_candidate_match_only",
                "evidence_source": self.source_name.value,
                "confidence": 0.5,
                "allowed_for_future_copy": False,
                "requires_verification": True,
                "risk_flag": "candidate_only_no_merge",
            },
        ]
