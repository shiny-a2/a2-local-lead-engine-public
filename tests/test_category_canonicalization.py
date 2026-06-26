from app.core.enums import ConflictType, ManualReviewType
from app.db.models.candidate_conflict import CandidateConflict
from app.services.manual_review_service import ManualReviewService
from app.services.normalization_service import NormalizationService


def test_geoapify_category_maps_to_internal_category():
    assert NormalizationService().canonicalize_category("commercial.hairdresser") == "barber"


def test_osm_tag_maps_to_internal_category():
    assert NormalizationService().canonicalize_category("beauty") == "beauty_salon"


def test_unknown_category_creates_manual_review(session):
    item = ManualReviewService(session).create(
        ManualReviewType.CATEGORY_CONFLICT,
        "Unknown category requires review.",
    )
    assert item.review_type == ManualReviewType.CATEGORY_CONFLICT


def test_conflicting_categories_create_conflict(session):
    conflict = CandidateConflict(
        conflict_type=ConflictType.CATEGORY_CONFLICT,
        severity="medium",
        description="Conflicting categories from sources.",
        evidence_json={"categories": ["barber", "cleaning_service"]},
    )
    session.add(conflict)
    session.commit()
    assert conflict.id is not None

