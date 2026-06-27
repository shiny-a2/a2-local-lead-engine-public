from app.services.contact_relevance_service import ContactRelevanceService


def test_drops_foreign_same_name_domain():
    ok, reason = ContactRelevanceService().is_plausible("Queen Nail", "New Zealand", "info@queennails.dk")
    assert ok is False
    assert "foreign" in reason


def test_drops_directory_aggregator_domains():
    svc = ContactRelevanceService()
    for name, email in [
        ("Ponsonby Nails", "info@findmylocal.nz"),
        ("Chil Body And Hair", "info@beautysalon.nz"),
        ("HealthElement", "info@beautycare.co.nz"),
    ]:
        ok, _ = svc.is_plausible(name, "New Zealand", email)
        assert ok is False


def test_keeps_own_domain_matching_business():
    svc = ContactRelevanceService()
    for name, email in [
        ("Tonic Room", "info@tonicroom.co.nz"),
        ("About Face", "info@aboutface.co.nz"),
    ]:
        ok, _ = svc.is_plausible(name, "New Zealand", email)
        assert ok is True


def test_filter_emails_keeps_only_plausible():
    kept = ContactRelevanceService().filter_emails(
        "Tonic Room", "New Zealand",
        ["info@tonicroom.co.nz", "info@findmylocal.nz", "info@queennails.dk"],
    )
    assert kept == ["info@tonicroom.co.nz"]
