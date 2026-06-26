from app.connectors.osm_overpass import OsmOverpassConnector
from app.services.email_deliverability_service import EmailDeliverabilityService
from app.services.geography_service import GeographyService
from app.services.openai_client import OpenAIClient
from app.settings import Settings


def test_geography_registry_loads_countries_and_cities():
    geo = GeographyService()
    countries = geo.countries()
    assert "New Zealand" in countries
    assert "Australia" in countries
    assert "Germany" in countries
    assert "Auckland" in geo.cities("New Zealand", "big")
    assert geo.cities("New Zealand", "small")
    # all = big + small, and no duplicates between sizes for this registry
    assert len(geo.cities("New Zealand", "all")) == len(
        geo.cities("New Zealand", "big")
    ) + len(geo.cities("New Zealand", "small"))
    assert geo.total_cities() > 100
    assert ("Australia", "Sydney") in geo.all_targets("big")


def test_geography_unknown_country_is_empty():
    geo = GeographyService()
    assert geo.cities("Atlantis") == []
    assert geo.country("Atlantis") is None


def test_osm_query_matches_local_and_english_city_name(test_settings):
    request = OsmOverpassConnector(test_settings).build_request(
        {
            "city": "Munich",
            "country": "Germany",
            "category": "beauty_salon",
            "osm_tag_key": "shop",
            "osm_tag_values": ["beauty"],
            "limit": 25,
        }
    )
    data = request.params["data"]
    # local-name area (kept for older behaviour) and the English-name area
    assert 'area["name"="Munich"]' in data
    assert 'area["name:en"="Munich"]' in data
    assert "out center 25" in data


def test_osm_query_uses_iso_country_code_when_provided(test_settings):
    request = OsmOverpassConnector(test_settings).build_request(
        {
            "city": "Hamilton",
            "country": "New Zealand",
            "country_code": "NZ",
            "category": "barber",
            "osm_tag_key": "shop",
            "osm_tag_values": ["hairdresser"],
            "limit": 25,
        }
    )
    data = request.params["data"]
    assert 'area["ISO3166-1"="NZ"]' in data
    assert "(area.country)" in data


def test_deliverability_service_reads_spf_dmarc_without_network():
    def fake_get(name, record_type="TXT"):
        if name == "good.com":
            return ["v=spf1 include:_spf.example.com ~all"]
        if name == "_dmarc.good.com":
            return ["v=DMARC1; p=quarantine;"]
        if name == "default._domainkey.good.com":
            return ["v=DKIM1; k=rsa; p=ABC"]
        return []

    result = EmailDeliverabilityService(http_get=fake_get).check_domain("good.com")
    assert result["spf"] == "present"
    assert result["dmarc"] == "present"
    assert "default" in result["dkim_selectors_found"]
    assert result["ready_for_cold_email"] is True


def test_deliverability_service_flags_missing_records():
    result = EmailDeliverabilityService(http_get=lambda *_args, **_kw: []).check_domain("bare.com")
    assert result["spf"] == "MISSING"
    assert result["dmarc"] == "MISSING"
    assert result["ready_for_cold_email"] is False


def test_openai_client_builds_request_and_parses_without_network():
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"drafts": []}'}}]}

    def fake_post(payload, headers):
        captured["payload"] = payload
        captured["headers"] = headers
        return FakeResponse()

    settings = Settings(openai_api_key="sk-test", openai_email_model="gpt-4o-mini")
    out = OpenAIClient(settings, http_post=fake_post).chat_json("system", "user")
    assert out == '{"drafts": []}'
    assert captured["payload"]["model"] == "gpt-4o-mini"
    assert captured["payload"]["response_format"] == {"type": "json_object"}
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
