from app.core.enums import NormalizationOperation
from app.services.candidate_builder_service import CandidateBuilderService
from app.services.candidate_quality_service import CandidateQualityService
from tests.phase3_helpers import make_raw_record


def _candidate(session, **kwargs):
    raw, _ = make_raw_record(session, **kwargs)
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    return builder.build_from_raw([raw], run, commit=True)[0]


def test_quality_score_calculated(session):
    candidate = _candidate(session)
    assert CandidateQualityService(session).score(candidate)["quality_score"] > 0


def test_ready_candidates_marked_ready_for_phase4(session):
    candidate = _candidate(session)
    CandidateQualityService(session).apply(candidate)
    assert candidate.status.value in {"READY_FOR_WEBSITE_VERIFICATION", "NEEDS_MANUAL_REVIEW"}


def test_low_quality_candidates_blocked(session):
    candidate = _candidate(session, name="Barber Shop", lat=None, lng=None, suburb=None)
    CandidateQualityService(session).apply(candidate)
    assert candidate.status.value != "READY_FOR_DRAFT"


def test_missing_name_handled(session):
    raw, _ = make_raw_record(session, name="")
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    assert builder.build_from_raw([raw], run, commit=True) == []


def test_missing_location_handled(session):
    candidate = _candidate(session, lat=None, lng=None, suburb=None)
    report = CandidateQualityService(session).score(candidate)
    assert report["location_score"] < 70


def test_high_chain_risk_blocks_readiness(session):
    candidate = _candidate(session, name="Example Group")
    candidate.chain_risk_score = 90
    CandidateQualityService(session).apply(candidate)
    assert candidate.status.value == "NEEDS_MANUAL_REVIEW"
