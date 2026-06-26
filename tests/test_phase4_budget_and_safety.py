from app.services.tavily_search_service import TavilySearchService


def test_disabled_live_api_calls_blocks_live_search(test_settings):
    allowed, reason = TavilySearchService(test_settings).can_execute(1)
    assert allowed is False
    assert reason == "LIVE_API_CALLS_DISABLED"


def test_disabled_website_verification_blocks_commit(test_settings):
    test_settings.live_api_calls_enabled = True
    test_settings.tavily_api_key = "present"
    allowed, reason = TavilySearchService(test_settings).can_execute(1)
    assert allowed is False
    assert reason == "WEBSITE_VERIFICATION_DISABLED"


def test_disabled_contact_verification_blocks_contact_commit(test_settings):
    assert test_settings.contact_verification_enabled is False


def test_tavily_budget_cap_blocks_run(test_settings):
    test_settings.live_api_calls_enabled = True
    test_settings.website_verification_enabled = True
    test_settings.tavily_api_key = "present"
    assert TavilySearchService(test_settings).can_execute(999)[1] == "TAVILY_BUDGET_EXCEEDED"


def test_url_probe_limits_enforced(test_settings):
    assert test_settings.url_probe_max_urls_per_candidate == 5

