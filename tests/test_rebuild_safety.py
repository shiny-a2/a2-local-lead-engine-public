from sqlalchemy import select

from app.core.enums import NormalizationOperation, NormalizationRunStatus
from app.db.models.candidate_business import CandidateBusiness
from app.services.candidate_builder_service import CandidateBuilderService
from tests.phase3_helpers import make_raw_record


def test_dry_run_does_not_write_candidates(session):
    raw, _ = make_raw_record(session)
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=True)
    builder.build_from_raw([raw], run, commit=False)
    assert session.scalars(select(CandidateBusiness)).all() == []
    assert run.status == NormalizationRunStatus.DRY_RUN_ONLY


def test_commit_writes_candidates(session):
    raw, _ = make_raw_record(session)
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    builder.build_from_raw([raw], run, commit=True)
    assert session.scalar(select(CandidateBusiness)) is not None


def test_raw_source_records_remain_unchanged(session):
    raw, _ = make_raw_record(session)
    before = raw.record_hash
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    builder.build_from_raw([raw], run, commit=True)
    assert raw.record_hash == before


def test_rebuild_operation_is_explicit(session):
    run = CandidateBuilderService(session).start_run(
        NormalizationOperation.REBUILD_CANDIDATES,
        dry_run=True,
    )
    assert run.operation == NormalizationOperation.REBUILD_CANDIDATES


def test_candidate_fingerprints_remain_stable_for_same_input(session):
    raw, _ = make_raw_record(session)
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    first = builder.build_from_raw([raw], run, commit=True)[0].candidate_identity_fingerprint
    second = session.scalar(select(CandidateBusiness)).candidate_identity_fingerprint
    assert first == second
