from pathlib import Path

from app.core.enums import Phase5Decision
from app.db.models.email_draft import EmailDraft
from app.db.models.email_send import EmailSend
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision as DecisionModel
from app.services.lead_scoring_service import LeadScoringService
from tests.phase5_helpers import make_phase5_candidate


def test_phase5_creates_no_outreach_artifacts(session):
    campaign, _ = make_phase5_candidate(session)
    LeadScoringService(session).score_candidates(campaign.slug, commit=True)
    assert session.query(EmailDraft).count() == 0
    assert session.query(EmailSend).count() == 0
    decisions = session.query(DecisionModel).all()
    assert all(row.decision in {Phase5Decision.READY_FOR_PHASE_6_INSIGHT, Phase5Decision.READY_FOR_PHASE_6_WITH_WARNINGS, Phase5Decision.HOLD_NO_SAFE_CONTACT, Phase5Decision.NEEDS_MANUAL_REVIEW, Phase5Decision.REJECT_INSUFFICIENT_PERSONALIZATION_EVIDENCE, Phase5Decision.REJECT_LOW_FIT} for row in decisions)


def test_no_forbidden_phase5_dependencies():
    text = "\n".join(path.read_text(encoding="utf-8") for path in Path("app/services").glob("*scoring*.py"))
    lowered = text.lower()
    assert "openai" not in lowered
    assert "tavily" not in lowered
    assert "smtp" not in lowered
    assert "google maps" not in lowered
