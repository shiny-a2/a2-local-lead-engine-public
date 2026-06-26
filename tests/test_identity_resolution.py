from app.services.identity_resolution_service import IdentityResolutionService
from tests.phase3_helpers import make_raw_record


def test_same_name_close_geo_same_category_auto_merge(session):
    a, _ = make_raw_record(session, name="Example Barber", lat=-36.85, lng=174.74)
    b, _ = make_raw_record(session, name="Example Barber", lat=-36.8501, lng=174.7401)
    assert IdentityResolutionService().score(a, b).decision == "AUTO_MERGE"


def test_same_name_far_geo_not_auto_merge(session):
    a, _ = make_raw_record(session, name="Example Barber A", lat=-36.85, lng=174.74)
    b, _ = make_raw_record(session, name="Example Barber A", lat=-37.0, lng=175.0)
    assert IdentityResolutionService().score(a, b).decision != "AUTO_MERGE"


def test_same_phone_strengthens_match(session):
    a, _ = make_raw_record(session, name="Example Barber B", phone="123")
    b, _ = make_raw_record(session, name="Example Barber B", phone="123")
    assert "exact_phone_match" in IdentityResolutionService().score(a, b).reasons


def test_different_category_weakens_match(session):
    a, _ = make_raw_record(session, name="Example Local", category="commercial.hairdresser")
    b, _ = make_raw_record(session, name="Example Local", category="service.cleaning")
    assert "different_category" in IdentityResolutionService().score(a, b).risk_flags


def test_generic_name_requires_stronger_evidence(session):
    a, _ = make_raw_record(session, name="Barber Shop", phone=None)
    b, _ = make_raw_record(session, name="Barber Shop", phone=None)
    assert "generic_name" in IdentityResolutionService().score(a, b).risk_flags


def test_branch_risk_prevents_auto_merge(session):
    a, _ = make_raw_record(
        session, name="Example Barber", suburb="Ponsonby", lat=-36.85, lng=174.74
    )
    b, _ = make_raw_record(
        session, name="Example Barber", suburb="Takapuna", lat=-36.78, lng=174.75
    )
    assert "possible_branch_split" in IdentityResolutionService().score(a, b).risk_flags


def test_chain_risk_prevents_auto_merge(session):
    a, _ = make_raw_record(session, name="Example Barber Group", lat=-36.85, lng=174.74)
    b, _ = make_raw_record(session, name="Example Barber Group", lat=-36.86, lng=174.75)
    assert IdentityResolutionService().score(a, b).decision != "AUTO_MERGE"
