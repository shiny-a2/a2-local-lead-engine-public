from app.core.enums import Phase4WebsiteStatus
from app.services.verified_evidence_service import VerifiedEvidenceService
from tests.test_candidate_quality import _candidate


def test_verified_social_only_evidence_created(session):
    rows = VerifiedEvidenceService().from_web_status(_candidate(session), Phase4WebsiteStatus.SOCIAL_ONLY)
    assert any(row["evidence_type"] == "verified_social_only" for row in rows)


def test_verified_directory_only_evidence_created(session):
    rows = VerifiedEvidenceService().from_web_status(_candidate(session), Phase4WebsiteStatus.DIRECTORY_ONLY)
    assert any(row["evidence_type"] == "verified_directory_only" for row in rows)


def test_verified_no_dedicated_website_probable_created_conservatively(session):
    rows = VerifiedEvidenceService().from_web_status(_candidate(session), Phase4WebsiteStatus.NO_WEBSITE_PROBABLE)
    item = [row for row in rows if row["evidence_type"] == "verified_no_dedicated_website_probable"][0]
    assert item["allowed_for_future_copy"] is True


def test_raw_email_phone_not_allowed_for_future_copy(session):
    rows = VerifiedEvidenceService().from_web_status(_candidate(session), Phase4WebsiteStatus.SOCIAL_ONLY)
    assert "raw_email" not in str(rows)
    assert "raw_phone" not in str(rows)


def test_no_email_subject_body_generated(session):
    rows = VerifiedEvidenceService().from_web_status(_candidate(session), Phase4WebsiteStatus.SOCIAL_ONLY)
    assert "subject" not in str(rows).lower()
    assert "body" not in str(rows).lower()

