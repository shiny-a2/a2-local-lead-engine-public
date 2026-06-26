from sqlalchemy import select

from app.core.enums import NormalizationOperation
from app.db.models.candidate_alias import CandidateAlias
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_source_link import CandidateSourceLink
from app.services.candidate_builder_service import CandidateBuilderService
from tests.phase3_helpers import make_raw_record


def test_raw_records_create_candidate(session):
    raw, _ = make_raw_record(session)
    service = CandidateBuilderService(session)
    run = service.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    candidates = service.build_from_raw([raw], run, commit=True)
    assert candidates[0].display_name == raw.raw_name


def test_raw_records_are_not_overwritten(session):
    raw, _ = make_raw_record(session)
    before = raw.raw_payload_json.copy()
    service = CandidateBuilderService(session)
    run = service.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    service.build_from_raw([raw], run, commit=True)
    assert raw.raw_payload_json == before


def test_source_links_created(session):
    raw, _ = make_raw_record(session)
    service = CandidateBuilderService(session)
    run = service.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    service.build_from_raw([raw], run, commit=True)
    assert session.scalar(select(CandidateSourceLink)) is not None


def test_aliases_created(session):
    raw, _ = make_raw_record(session)
    service = CandidateBuilderService(session)
    run = service.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    service.build_from_raw([raw], run, commit=True)
    assert session.scalar(select(CandidateAlias)) is not None


def test_candidate_identity_fingerprint_stable(session):
    raw, _ = make_raw_record(session)
    service = CandidateBuilderService(session)
    run = service.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    candidate = service.build_from_raw([raw], run, commit=True)[0]
    again = session.get(CandidateBusiness, candidate.id)
    assert candidate.candidate_identity_fingerprint == again.candidate_identity_fingerprint
