from app.settings import Settings


class DraftVariantService:
    def labels(self, settings: Settings) -> list[str]:
        return ["A", "B"][: settings.email_generation_max_variants_per_candidate]
