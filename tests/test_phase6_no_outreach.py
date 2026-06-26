from pathlib import Path

from app.db.models.email_draft import EmailDraft
from app.db.models.email_send import EmailSend
from app.services.business_insight_orchestrator_service import BusinessInsightOrchestratorService
from tests.phase6_helpers import make_phase6_ready_candidate


def test_phase6_creates_no_email_or_send_records(session):
    campaign, _ = make_phase6_ready_candidate(session)
    BusinessInsightOrchestratorService(session).run(campaign.slug, commit=True)
    assert session.query(EmailDraft).count() == 0
    assert session.query(EmailSend).count() == 0


def test_phase6_services_have_no_forbidden_integrations():
    text = "\n".join(path.read_text(encoding="utf-8") for path in Path("app/services").glob("*offer*.py"))
    lowered = text.lower()
    assert "openai" not in lowered
    assert "smtp" not in lowered
    assert "tavily" not in lowered
    assert "google maps" not in lowered
