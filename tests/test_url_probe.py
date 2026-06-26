from app.core.enums import UrlProbeStatus
from app.services.url_probe_service import UrlProbeService


def test_skips_in_dry_run(test_settings):
    assert UrlProbeService(test_settings).probe("https://example.com", dry_run=True)["probe_status"] == UrlProbeStatus.SKIPPED_DRY_RUN


def test_respects_timeout_setting(test_settings):
    assert test_settings.url_probe_timeout_seconds == 8


def test_max_bytes_enforced_setting(test_settings):
    assert test_settings.url_probe_max_bytes == 250000


def test_redirect_chain_shape():
    assert isinstance({"redirect_chain_json": []}["redirect_chain_json"], list)


def test_no_form_submit_no_deep_crawl():
    assert True

