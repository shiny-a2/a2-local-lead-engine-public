from app.services.country_compliance_service import CountryComplianceService


def test_nz_au_allow_cold_b2b():
    svc = CountryComplianceService()
    for country in ("New Zealand", "Australia"):
        result = svc.evaluate(country)
        assert result["allowed"] is True
        assert result["consent_model"] == "inferred_b2b"
        assert result["requires_unsubscribe"] is True


def test_eu_and_turkey_block_cold_email():
    svc = CountryComplianceService()
    for country in ("Germany", "France", "Ireland", "Turkey", "Spain", "Italy"):
        result = svc.evaluate(country)
        assert result["allowed"] is False
        assert result["consent_model"] == "opt_in_required"
        assert result["block_reason"]


def test_us_is_opt_out_with_physical_address():
    result = CountryComplianceService().evaluate("United States")
    assert result["allowed"] is True
    assert result["consent_model"] == "opt_out"
    assert result["requires_physical_address"] is True


def test_unknown_country_blocked_by_default():
    result = CountryComplianceService().evaluate("Atlantis")
    assert result["allowed"] is False
    assert result["risk"] == "high"
