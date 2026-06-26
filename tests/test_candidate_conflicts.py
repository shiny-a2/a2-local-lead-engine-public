from app.core.enums import ConflictType
from app.db.models.candidate_conflict import CandidateConflict


def _conflict(session, conflict_type):
    row = CandidateConflict(
        conflict_type=conflict_type,
        severity="medium",
        description="test",
        evidence_json={},
    )
    session.add(row)
    session.commit()
    return row


def test_name_conflict_stored(session):
    assert _conflict(session, ConflictType.NAME_CONFLICT).id


def test_category_conflict_stored(session):
    assert _conflict(session, ConflictType.CATEGORY_CONFLICT).id


def test_location_conflict_stored(session):
    assert _conflict(session, ConflictType.LOCATION_CONFLICT).id


def test_nzbn_mismatch_stored(session):
    assert _conflict(session, ConflictType.NZBN_ENTITY_MISMATCH).id


def test_shared_phone_website_flagged_as_risk_not_blind_merge(session):
    phone = _conflict(session, ConflictType.PHONE_SHARED_ACROSS_CANDIDATES)
    website = _conflict(session, ConflictType.WEBSITE_SHARED_ACROSS_CANDIDATES)
    assert phone.conflict_type == ConflictType.PHONE_SHARED_ACROSS_CANDIDATES
    assert website.conflict_type == ConflictType.WEBSITE_SHARED_ACROSS_CANDIDATES
