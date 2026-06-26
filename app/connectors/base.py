from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.core.enums import SourceName
from app.core.fingerprints import stable_fingerprint
from app.settings import Settings


@dataclass(frozen=True)
class ConnectorRequest:
    url: str
    params: dict[str, Any]
    request_key: str


@dataclass(frozen=True)
class ConfigCheck:
    ready: bool
    reason: str


class BaseConnector(ABC):
    source_name: SourceName

    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def check_config(self) -> ConfigCheck:
        raise NotImplementedError

    @abstractmethod
    def estimate_cost_or_credits(self, params: dict[str, Any]) -> int:
        raise NotImplementedError

    @abstractmethod
    def build_request(self, params: dict[str, Any]) -> ConnectorRequest:
        raise NotImplementedError

    def execute(self, request: ConnectorRequest, dry_run: bool) -> dict[str, Any]:
        if dry_run:
            return {"dry_run": True, "request": request.params, "features": []}
        raise RuntimeError("Live execution is intentionally guarded by collection services.")

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        return response

    @abstractmethod
    def extract_raw_records(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def extract_personalization_evidence(self, raw_record: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError

    def fingerprint(self, record: dict[str, Any]) -> str:
        return stable_fingerprint(
            {
                "source": self.source_name.value,
                "external_id": record.get("source_external_id"),
                "name": record.get("raw_name"),
                "lat": record.get("raw_lat"),
                "lng": record.get("raw_lng"),
            }
        )
