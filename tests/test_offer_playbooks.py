from app.core.enums import OfferPlaybookStatus
from app.db.models.offer_playbook import OfferPlaybook
from app.services.category_playbook_service import CategoryPlaybookService


def test_initial_playbooks_seeded(session):
    service = CategoryPlaybookService(session)
    service.seed_defaults()
    assert service.active_for_category("beauty_salon") is not None
    assert service.active_for_category("barber") is not None
    assert service.active_for_category("cleaning_service") is not None
    cafe = session.query(OfferPlaybook).filter_by(category="cafe").one()
    assert cafe.status != OfferPlaybookStatus.ACTIVE


def test_playbook_version_stored(session):
    service = CategoryPlaybookService(session)
    service.seed_defaults()
    assert service.active_for_category("barber").version == "v1.0"
