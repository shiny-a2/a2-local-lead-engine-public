from app.core.enums import Phase4WebsiteStatus, VerificationRunOperation
from app.db.models.verification_run import VerificationRun
from app.services.website_verification_service import WebsiteVerificationService
from tests.test_candidate_quality import _candidate


def _run(session):
    row = VerificationRun(
        run_id="test-phase4-run",
        operation=VerificationRunOperation.PHASE4_FULL_REVIEW,
        dry_run=False,
    )
    session.add(row)
    session.commit()
    return row


def test_website_found_official(session, test_settings):
    candidate = _candidate(session, name="Strong Barber")
    row = WebsiteVerificationService(test_settings, session).verify_from_results(candidate, _run(session).id, [{"url": "https://strongbarber.co.nz", "title": "Strong Barber Auckland"}])
    assert row.website_status == Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL


def test_social_only(session, test_settings):
    candidate = _candidate(session, name="Social Barber")
    row = WebsiteVerificationService(test_settings, session).verify_from_results(candidate, _run(session).id, [{"url": "https://facebook.com/socialbarber", "title": "Social Barber"}])
    assert row.website_status == Phase4WebsiteStatus.SOCIAL_ONLY


def test_directory_only(session, test_settings):
    candidate = _candidate(session)
    row = WebsiteVerificationService(test_settings, session).verify_from_results(candidate, _run(session).id, [{"url": "https://yellow.co.nz/x", "title": "Example"}])
    assert row.website_status == Phase4WebsiteStatus.DIRECTORY_ONLY


def test_no_website_probable_with_conservative_evidence(session, test_settings):
    candidate = _candidate(session)
    row = WebsiteVerificationService(test_settings, session).verify_from_results(candidate, _run(session).id, [{"url": "https://unknown1.co.nz"}, {"url": "https://unknown2.co.nz"}])
    assert row.website_status == Phase4WebsiteStatus.NO_WEBSITE_PROBABLE
    assert "couldn't find" in row.no_website_claim_text


def test_raw_website_missing_alone_insufficient(session, test_settings):
    row = WebsiteVerificationService(test_settings, session).verify_from_results(_candidate(session), _run(session).id, [])
    assert row.website_status == Phase4WebsiteStatus.INSUFFICIENT_EVIDENCE
