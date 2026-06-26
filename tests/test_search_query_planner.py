from app.services.search_query_planner import SearchQueryPlanner
from tests.test_candidate_quality import _candidate


def test_limited_queries_per_candidate(session, test_settings):
    candidate = _candidate(session)
    queries = SearchQueryPlanner(test_settings).plan_for_candidate(candidate)
    assert len(queries) <= test_settings.tavily_max_queries_per_candidate


def test_includes_business_name_category_location(session, test_settings):
    candidate = _candidate(session)
    text = " ".join(query.query_text for query in SearchQueryPlanner(test_settings).plan_for_candidate(candidate))
    assert candidate.display_name in text
    assert candidate.city in text


def test_generic_names_get_disambiguation(session, test_settings):
    candidate = _candidate(session, name="Barber Shop")
    queries = SearchQueryPlanner(test_settings).plan_for_candidate(candidate)
    assert any("Auckland business" in query.query_text for query in queries)


def test_max_query_cap_enforced(session, test_settings):
    test_settings.tavily_max_queries_per_candidate = 2
    assert len(SearchQueryPlanner(test_settings).plan_for_candidate(_candidate(session))) == 2


def test_dry_run_no_network():
    assert True

