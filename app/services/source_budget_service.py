from dataclasses import dataclass

from app.core.enums import SourceName
from app.settings import Settings


@dataclass(frozen=True)
class BudgetCheck:
    allowed: bool
    reason: str


class SourceBudgetService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def check(self, source_name: SourceName, *, limit: int, request_count: int = 1) -> BudgetCheck:
        if limit > self.settings.max_leads_per_run:
            return BudgetCheck(False, "MAX_LEADS_PER_RUN_EXCEEDED")
        if limit > self.settings.phase2_max_raw_records_per_run:
            return BudgetCheck(False, "PHASE2_MAX_RAW_RECORDS_PER_RUN_EXCEEDED")
        if source_name == SourceName.GEOAPIFY:
            if request_count > self.settings.geoapify_max_requests_per_run:
                return BudgetCheck(False, "GEOAPIFY_MAX_REQUESTS_PER_RUN_EXCEEDED")
            if request_count > self.settings.geoapify_daily_credit_budget:
                return BudgetCheck(False, "GEOAPIFY_DAILY_CREDIT_BUDGET_EXCEEDED")
        if (
            source_name == SourceName.OSM_OVERPASS
            and request_count > self.settings.osm_max_requests_per_run
        ):
            return BudgetCheck(False, "OSM_MAX_REQUESTS_PER_RUN_EXCEEDED")
        if (
            source_name == SourceName.NZBN
            and request_count > self.settings.nzbn_max_requests_per_run
        ):
            return BudgetCheck(False, "NZBN_MAX_REQUESTS_PER_RUN_EXCEEDED")
        return BudgetCheck(True, "BUDGET_OK")
