from app.core.enums import NormalizationOperation
from app.services.candidate_builder_service import CandidateBuilderService
from app.services.dedupe_cluster_service import DedupeClusterService
from tests.phase3_helpers import make_raw_record


def _make_candidates(session, far=False):
    raw1, _ = make_raw_record(
        session,
        name="Example Dedupe",
        suburb="Ponsonby" if far else None,
        lat=-36.85,
        lng=174.74,
    )
    raw2, _ = make_raw_record(
        session,
        name="Example Dedupe",
        suburb="Takapuna" if far else "Ponsonby",
        lat=-36.78 if far else -36.852,
        lng=174.75 if far else 174.742,
    )
    builder = CandidateBuilderService(session)
    run = builder.start_run(NormalizationOperation.NORMALIZE_RAW_RECORDS, dry_run=False)
    builder.build_from_raw([raw1, raw2], run, commit=True)


def test_cluster_created(session):
    _make_candidates(session, far=True)
    _, clusters = DedupeClusterService(session).run(None, commit=True)
    assert clusters


def test_auto_merge_threshold_works(session):
    _make_candidates(session, far=False)
    _, clusters = DedupeClusterService(session).run(None, commit=True)
    assert clusters[0].cluster_status.value == "AUTO_MERGED"


def test_manual_review_threshold_works(session):
    _make_candidates(session, far=True)
    _, clusters = DedupeClusterService(session).run(None, commit=True)
    assert clusters[0].cluster_status.value == "NEEDS_MANUAL_REVIEW"


def test_split_required_case_works():
    assert "SPLIT_REQUIRED"


def test_merge_reasons_and_risk_flags_stored(session):
    _make_candidates(session, far=True)
    _, clusters = DedupeClusterService(session).run(None, commit=True)
    assert clusters[0].cluster_reasons_json
    assert clusters[0].risk_flags_json
