import pytest

from app.core.enums import ReviewLockStatus
from app.services.review_lock_service import ReviewLockService
from tests.phase9_helpers import make_phase9_queue_item


def test_lock_prevents_concurrent_edit(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    service = ReviewLockService(session, settings)
    service.lock(item.id, "Amirali")
    with pytest.raises(ValueError):
        service.lock(item.id, "Other")


def test_unlock_releases_lock(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    service = ReviewLockService(session, settings)
    lock = service.lock(item.id, "Amirali")
    service.unlock(item.id, "Amirali")
    assert lock.status == ReviewLockStatus.RELEASED
