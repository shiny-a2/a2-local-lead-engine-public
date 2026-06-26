from app.core.enums import SourceName
from app.services.source_budget_service import SourceBudgetService


def test_run_over_max_request_budget_is_blocked(test_settings):
    result = SourceBudgetService(test_settings).check(
        SourceName.NZBN, limit=10, request_count=999
    )
    assert result.allowed is False


def test_limit_over_max_leads_per_run_is_blocked(test_settings):
    result = SourceBudgetService(test_settings).check(
        SourceName.GEOAPIFY, limit=999, request_count=1
    )
    assert result.allowed is False


def test_geoapify_budget_guard_works(test_settings):
    result = SourceBudgetService(test_settings).check(
        SourceName.GEOAPIFY, limit=10, request_count=21
    )
    assert result.allowed is False


def test_osm_request_cap_works(test_settings):
    result = SourceBudgetService(test_settings).check(
        SourceName.OSM_OVERPASS, limit=10, request_count=6
    )
    assert result.allowed is False


def test_nzbn_cap_works(test_settings):
    result = SourceBudgetService(test_settings).check(
        SourceName.NZBN, limit=10, request_count=51
    )
    assert result.allowed is False
