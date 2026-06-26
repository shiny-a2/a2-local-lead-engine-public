from dataclasses import dataclass

from app.core.enums import SearchQueryType
from app.db.models.candidate_business import CandidateBusiness
from app.settings import Settings


@dataclass(frozen=True)
class PlannedSearchQuery:
    query_text: str
    query_type: SearchQueryType
    cache_key: str


class SearchQueryPlanner:
    def __init__(self, settings: Settings):
        self.settings = settings

    def plan_for_candidate(self, candidate: CandidateBusiness) -> list[PlannedSearchQuery]:
        base = " ".join(
            part for part in [candidate.display_name, candidate.suburb, candidate.city] if part
        )
        queries = [
            PlannedSearchQuery(
                f"{base} official website",
                SearchQueryType.OFFICIAL_WEBSITE_SEARCH,
                f"official:{candidate.id}",
            ),
            PlannedSearchQuery(
                f"{base} contact",
                SearchQueryType.CONTACT_SEARCH,
                f"contact:{candidate.id}",
            ),
            PlannedSearchQuery(
                f"{base} {candidate.canonical_category}",
                SearchQueryType.BRAND_DISAMBIGUATION_SEARCH,
                f"brand:{candidate.id}",
            ),
        ]
        if candidate.generic_name_risk_score >= 80:
            queries.append(
                PlannedSearchQuery(
                    f"{base} {candidate.address_line or ''} Auckland business",
                    SearchQueryType.BRAND_DISAMBIGUATION_SEARCH,
                    f"generic:{candidate.id}",
                )
            )
        return queries[: self.settings.tavily_max_queries_per_candidate]

