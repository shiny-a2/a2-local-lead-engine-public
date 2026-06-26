from app.core.enums import ComplexityLevel
from app.db.models.offer_module import OfferModule


class ModuleSelectionService:
    def select(self, modules: list[OfferModule]) -> tuple[list[OfferModule], list[OfferModule]]:
        selected = [
            module
            for module in modules
            if module.is_core and module.implementation_complexity != ComplexityLevel.HIGH
        ]
        excluded = [module for module in modules if module not in selected]
        return selected, excluded
