from app.core.enums import ManualReviewType
from app.services.manual_review_service import ManualReviewService


def test_ambiguous_duplicate_creates_review_item(session):
    item = ManualReviewService(session).create(ManualReviewType.AMBIGUOUS_DUPLICATE, "Ambiguous")
    assert item.review_type == ManualReviewType.AMBIGUOUS_DUPLICATE


def test_chain_risk_creates_review_item(session):
    item = ManualReviewService(session).create(ManualReviewType.CHAIN_RISK, "Chain risk")
    assert item.review_type == ManualReviewType.CHAIN_RISK


def test_branch_risk_creates_review_item(session):
    item = ManualReviewService(session).create(ManualReviewType.BRANCH_RISK, "Branch risk")
    assert item.review_type == ManualReviewType.BRANCH_RISK


def test_category_conflict_creates_review_item(session):
    item = ManualReviewService(session).create(ManualReviewType.CATEGORY_CONFLICT, "Conflict")
    assert item.review_type == ManualReviewType.CATEGORY_CONFLICT


def test_generic_name_risk_creates_review_item(session):
    item = ManualReviewService(session).create(ManualReviewType.GENERIC_NAME_RISK, "Generic")
    assert item.review_type == ManualReviewType.GENERIC_NAME_RISK

