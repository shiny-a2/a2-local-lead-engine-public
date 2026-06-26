from app.services.email_generation_budget_service import EmailGenerationBudgetService
from app.settings import Settings


def test_budget_limits():
    service = EmailGenerationBudgetService(Settings(email_generation_max_candidates_per_run=1))
    allowed, reason = service.check(2, 1)
    assert allowed is False
    assert "CANDIDATES" in reason
