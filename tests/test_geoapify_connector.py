from app.connectors.geoapify import GeoapifyPlacesConnector
from app.core.enums import SensitiveOperation
from app.core.safety import check_operation


def test_geoapify_dry_run_does_not_call_network(test_settings):
    connector = GeoapifyPlacesConnector(test_settings)
    request = connector.build_request(
        {
            "city": "Auckland",
            "country": "New Zealand",
            "category": "barber",
            "source_category": "commercial.hairdresser",
            "limit": 5,
        }
    )
    response = connector.execute(request, dry_run=True)
    assert response["dry_run"] is True


def test_geoapify_missing_api_key_returns_config_gap(test_settings):
    assert (
        GeoapifyPlacesConnector(test_settings).check_config().reason
        == "GEOAPIFY_API_KEY_MISSING"
    )


def test_geoapify_disabled_live_flags_block_execution(test_settings):
    assert check_operation(test_settings, SensitiveOperation.LIVE_API_CALL).allowed is False
    assert check_operation(test_settings, SensitiveOperation.LEAD_COLLECTION).allowed is False


def test_geoapify_fixture_response_parses_raw_records(test_settings):
    connector = GeoapifyPlacesConnector(test_settings)
    records = connector.extract_raw_records(
        {
            "features": [
                {
                    "properties": {
                        "place_id": "p1",
                        "name": "Example Auckland Barber Studio",
                        "categories": ["commercial.hairdresser"],
                        "suburb": "Ponsonby",
                        "city": "Auckland",
                        "country": "New Zealand",
                        "contact": {"phone": "123"},
                    },
                    "geometry": {"coordinates": [174.7, -36.8]},
                }
            ]
        }
    )
    assert records[0]["raw_name"] == "Example Auckland Barber Studio"
    evidence = connector.extract_personalization_evidence(records[0])
    assert {item["evidence_type"] for item in evidence} >= {"business_name", "category_hint"}


def test_geoapify_fingerprint_stable(test_settings):
    connector = GeoapifyPlacesConnector(test_settings)
    record = {"source_external_id": "p1", "raw_name": "Name", "raw_lat": 1, "raw_lng": 2}
    assert connector.fingerprint(record) == connector.fingerprint(record)
