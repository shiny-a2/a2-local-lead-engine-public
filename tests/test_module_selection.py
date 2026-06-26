from app.services.category_playbook_service import CategoryPlaybookService
from app.services.module_selection_service import ModuleSelectionService


def test_category_modules_selected(session):
    service = CategoryPlaybookService(session)
    service.seed_defaults()
    barber = service.active_for_category("barber")
    selected, _ = ModuleSelectionService().select(service.modules_for(barber.id))
    slugs = {module.module_slug for module in selected}
    assert {"services-prices", "booking-request", "gallery", "directions"} <= slugs


def test_high_complexity_not_default(session):
    service = CategoryPlaybookService(session)
    service.seed_defaults()
    playbook = service.active_for_category("beauty_salon")
    selected, _ = ModuleSelectionService().select(service.modules_for(playbook.id))
    assert all(module.implementation_complexity.value != "HIGH" for module in selected)
