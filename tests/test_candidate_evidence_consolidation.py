from app.core.enums import NormalizationOperation
from app.services.candidate_builder_service import CandidateBuilderService
from app.services.candidate_evidence_service import CandidateEvidenceService
from tests.phase3_helpers import make_raw_record


def _candidate(session):
    raw, _ = make_raw_record(session, email="raw@example.test", phone="123")
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    return builder.build_from_raw([raw], run, commit=True)[0]


def test_business_category_suburb_evidence_consolidated(session):
    rows = CandidateEvidenceService(session).consolidate_for_candidate(_candidate(session).id)
    assert {"business_name", "category_hint", "suburb_hint"}.issubset(
        {row["evidence_type"] for row in rows}
    )


def test_supporting_raw_ids_stored(session):
    row = CandidateEvidenceService(session).consolidate_for_candidate(_candidate(session).id)[0]
    assert row["supporting_raw_record_ids_json"]


def test_website_field_missing_remains_requires_verification(session):
    rows = CandidateEvidenceService(session).consolidate_for_candidate(_candidate(session).id)
    item = [row for row in rows if row["evidence_type"] == "website_field_missing"][0]
    assert item["requires_verification"] is True
    assert item["allowed_for_future_copy"] is False


def test_raw_email_not_allowed_for_future_copy(session):
    rows = CandidateEvidenceService(session).consolidate_for_candidate(_candidate(session).id)
    item = [row for row in rows if row["evidence_type"] == "email_present_raw"][0]
    assert item["allowed_for_future_copy"] is False


def test_raw_phone_not_allowed_for_future_copy(session):
    rows = CandidateEvidenceService(session).consolidate_for_candidate(_candidate(session).id)
    item = [row for row in rows if row["evidence_type"] == "phone_present"][0]
    assert item["allowed_for_future_copy"] is False


def test_no_email_body_or_subject_generated(session):
    rows = CandidateEvidenceService(session).consolidate_for_candidate(_candidate(session).id)
    assert "subject" not in str(rows).lower()
    assert "body" not in str(rows).lower()

