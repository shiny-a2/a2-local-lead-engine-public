from app.connectors.osm_overpass import OsmOverpassConnector
from app.core.enums import SourceName
from app.services.source_budget_service import SourceBudgetService


def test_osm_builds_bounded_overpass_query(test_settings):
    request = OsmOverpassConnector(test_settings).build_request(
        {
            "city": "Auckland",
            "country": "New Zealand",
            "category": "barber",
            "osm_tag_key": "shop",
            "osm_tag_values": ["hairdresser"],
            "limit": 25,
        }
    )
    assert 'area["name"="Auckland"]' in request.params["data"]
    assert "out center 25" in request.params["data"]


def test_osm_dry_run_does_not_call_network(test_settings):
    connector = OsmOverpassConnector(test_settings)
    request = connector.build_request(
        {
            "city": "Auckland",
            "country": "New Zealand",
            "category": "barber",
            "osm_tag_key": "shop",
            "osm_tag_values": ["hairdresser"],
            "limit": 1,
        }
    )
    assert connector.execute(request, dry_run=True)["dry_run"] is True


def test_osm_budget_guard_blocks_too_many_requests(test_settings):
    result = SourceBudgetService(test_settings).check(
        SourceName.OSM_OVERPASS, limit=10, request_count=99
    )
    assert result.allowed is False


def test_osm_fixture_response_parses_tags_safely(test_settings):
    records = OsmOverpassConnector(test_settings).extract_raw_records(
        {
            "elements": [
                {
                    "type": "node",
                    "id": 1,
                    "lat": -36.8,
                    "lon": 174.7,
                    "tags": {
                        "name": "Sample Beauty Lounge Auckland",
                        "shop": "beauty",
                        "contact:email": "raw@example.test",
                        "website": "https://example.test",
                    },
                }
            ]
        }
    )
    assert records[0]["raw_email"] == "raw@example.test"
    evidence = OsmOverpassConnector(test_settings).extract_personalization_evidence(records[0])
    email_ev = [item for item in evidence if item["evidence_type"] == "email_present_raw"][0]
    assert email_ev["allowed_for_future_copy"] is False
