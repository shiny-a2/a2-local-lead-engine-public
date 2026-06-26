from app.core.enums import FeasibilityLevel
from app.db.models.implementation_feasibility_note import ImplementationFeasibilityNote
from app.services.business_insight_orchestrator_service import BusinessInsightOrchestratorService
from tests.phase6_helpers import make_phase6_ready_candidate


def test_feasibility_notes_created(session):
    campaign, _ = make_phase6_ready_candidate(session)
    run = BusinessInsightOrchestratorService(session).run(campaign.slug, commit=True)
    notes = session.query(ImplementationFeasibilityNote).filter_by(insight_run_id=run.id).all()
    assert notes
    assert all(note.feasibility_level in {FeasibilityLevel.EASY, FeasibilityLevel.MODERATE} for note in notes)
