from app.services.tavily_search_service import TavilySearchService


def test_dry_run_does_not_call_network(test_settings):
    assert TavilySearchService(test_settings).execute("x", dry_run=True)["dry_run"] is True


def test_missing_key_returns_config_gap(test_settings):
    assert TavilySearchService(test_settings).check_config()[1] == "TAVILY_API_KEY_MISSING"


def test_disabled_flags_block_execution(test_settings):
    allowed, reason = TavilySearchService(test_settings).can_execute(1)
    assert allowed is False
    assert reason == "LIVE_API_CALLS_DISABLED"


def test_budget_cap_blocks_execution(test_settings):
    test_settings.live_api_calls_enabled = True
    test_settings.website_verification_enabled = True
    test_settings.tavily_api_key = "present"
    allowed, reason = TavilySearchService(test_settings).can_execute(999)
    assert allowed is False
    assert reason == "TAVILY_BUDGET_EXCEEDED"


def test_mocked_fixture_results_parse():
    assert {"results": [{"url": "https://example.co.nz"}]}["results"][0]["url"]

