from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.services.claim_usage_service import ClaimUsageService
from app.services.email_input_assembler_service import EmailInputAssemblerService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_claim_usage_allowed_and_blocked(session):
    _, candidate = make_phase7_ready_candidate(session)
    phase6 = session.query(Phase6CandidateDecision).filter_by(candidate_business_id=candidate.id).one()
    row = EmailInputAssemblerService(session, Settings()).assemble(1, candidate, phase6)
    body = row.allowed_claims_json[0] + " you don't have a website"
    usages = ClaimUsageService().usages(1, body, row)
    assert any(item.allowed for item in usages)
    assert any(not item.allowed for item in usages)
