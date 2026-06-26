from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.services.email_input_assembler_service import EmailInputAssemblerService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_input_assembler_safe_snapshot(session):
    campaign, candidate = make_phase7_ready_candidate(session)
    phase6 = session.query(Phase6CandidateDecision).filter_by(candidate_business_id=candidate.id).one()
    row = EmailInputAssemblerService(session, Settings()).assemble(1, candidate, phase6)
    assert row.input_snapshot_hash
    assert row.offer_blocks_json
    assert "raw_phone" not in row.input_snapshot_json
    assert "opening_hours" not in row.input_snapshot_json
    assert row.blocked_claims_json
