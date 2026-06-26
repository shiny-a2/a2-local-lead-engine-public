from app.connectors.nzbn import NzbnConnector


def test_nzbn_dry_run_does_not_call_network(test_settings):
    connector = NzbnConnector(test_settings)
    request = connector.build_request({"query_name": "Example Auckland Barber Studio"})
    assert connector.execute(request, dry_run=True)["dry_run"] is True


def test_nzbn_missing_key_returns_config_gap(test_settings):
    assert NzbnConnector(test_settings).check_config().reason == "NZBN_API_KEY_MISSING"


def test_nzbn_fixture_parses_candidate_matches(test_settings):
    matches = NzbnConnector(test_settings).extract_candidate_matches(
        {"items": [{"nzbn": "123", "entityName": "Example Limited", "entityStatus": "Registered"}]},
        "Example",
    )
    assert matches[0]["entity_name"] == "Example Limited"


def test_nzbn_does_not_mark_record_send_ready(test_settings):
    evidence = NzbnConnector(test_settings).extract_personalization_evidence(
        {"entity_name": "Example Limited"}
    )
    assert all(item["requires_verification"] for item in evidence)

