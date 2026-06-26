from app.services.website_ownership_service import WebsiteOwnershipService
from tests.test_candidate_quality import _candidate


def test_high_confidence_official_website(session):
    candidate = _candidate(session, name="Example Barber")
    score, _, risks = WebsiteOwnershipService().confidence(candidate, {"url": "https://examplebarber.co.nz", "title": "Example Barber Auckland"})
    assert score >= 50
    assert "social_or_directory_not_official" not in risks


def test_unclear_ownership_manual_review(session):
    score, _, risks = WebsiteOwnershipService().confidence(_candidate(session), {"url": "https://unknown.co.nz", "title": "Other"})
    assert score < 50 or "unclear_ownership" in risks


def test_location_mismatch_lowers_confidence(session):
    candidate = _candidate(session)
    score, _, _ = WebsiteOwnershipService().confidence(candidate, {"url": "https://other.co.nz", "title": "Other Wellington"})
    assert score < 70


def test_social_directory_cannot_be_official(session):
    score, _, risks = WebsiteOwnershipService().confidence(_candidate(session), {"url": "https://facebook.com/x"})
    assert score == 0
    assert risks


def test_parked_broken_lowers_confidence(session):
    score, _, risks = WebsiteOwnershipService().confidence(_candidate(session), {"url": "https://parked.com", "title": "domain for sale"})
    assert score < 50
    assert risks
