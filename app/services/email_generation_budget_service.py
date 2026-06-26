from app.settings import Settings


class EmailGenerationBudgetService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def check(self, candidate_count: int, variants: int) -> tuple[bool, str]:
        if candidate_count > self.settings.email_generation_max_candidates_per_run:
            return False, "EMAIL_GENERATION_MAX_CANDIDATES_PER_RUN_EXCEEDED"
        if variants > self.settings.email_generation_max_variants_per_candidate:
            return False, "EMAIL_GENERATION_MAX_VARIANTS_PER_CANDIDATE_EXCEEDED"
        return True, "OK"

    def estimate_tokens(self, candidate_count: int, variants: int) -> int:
        return candidate_count * variants * min(self.settings.openai_email_max_tokens, 900)
