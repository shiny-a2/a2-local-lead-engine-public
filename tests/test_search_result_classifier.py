from app.core.enums import SearchResultType
from app.services.search_result_classifier import SearchResultClassifier
from tests.test_candidate_quality import _candidate


def test_official_candidate_website_classified(session):
    candidate = _candidate(session, name="Example Barber")
    result, _ = SearchResultClassifier().classify({"url": "https://examplebarber.co.nz", "title": "Example Barber Auckland"}, candidate)
    assert result == SearchResultType.POSSIBLE_OFFICIAL_WEBSITE


def test_social_profile_classified(session):
    result, _ = SearchResultClassifier().classify({"url": "https://facebook.com/x"}, _candidate(session))
    assert result == SearchResultType.SOCIAL_PROFILE


def test_directory_listing_classified(session):
    result, _ = SearchResultClassifier().classify({"url": "https://yellow.co.nz/x"}, _candidate(session))
    assert result == SearchResultType.DIRECTORY_LISTING


def test_booking_platform_classified(session):
    result, _ = SearchResultClassifier().classify({"url": "https://fresha.com/x"}, _candidate(session))
    assert result == SearchResultType.BOOKING_PAGE


def test_irrelevant_result_classified(session):
    result, _ = SearchResultClassifier().classify({"url": "https://x.co.nz", "snippet": "unrelated"}, _candidate(session))
    assert result == SearchResultType.IRRELEVANT
