from app.connectors.geoapify import GeoapifyPlacesConnector


def test_evidence_rows_created_for_core_fields(test_settings):
    evidence = GeoapifyPlacesConnector(test_settings).extract_personalization_evidence(
        {
            "raw_name": "Example Auckland Barber Studio",
            "raw_category": "barber",
            "raw_suburb": "Ponsonby",
            "raw_city": "Auckland",
        }
    )
    assert {"business_name", "category_hint", "suburb_hint", "website_field_missing"}.issubset(
        {item["evidence_type"] for item in evidence}
    )


def test_website_field_missing_requires_verification(test_settings):
    evidence = GeoapifyPlacesConnector(test_settings).extract_personalization_evidence({})
    item = [row for row in evidence if row["evidence_type"] == "website_field_missing"][0]
    assert item["requires_verification"] is True


def test_email_present_raw_is_not_allowed_for_outreach(test_settings):
    evidence = GeoapifyPlacesConnector(test_settings).extract_personalization_evidence(
        {"raw_email": "raw@example.test"}
    )
    item = [row for row in evidence if row["evidence_type"] == "email_present_raw"][0]
    assert item["allowed_for_future_copy"] is False
    assert item["risk_flag"] == "not_outreach_permission"


def test_no_email_body_or_subject_is_generated(test_settings):
    evidence = GeoapifyPlacesConnector(test_settings).extract_personalization_evidence(
        {"raw_name": "Example"}
    )
    assert "subject" not in str(evidence).lower()
    assert "body" not in str(evidence).lower()
