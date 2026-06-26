from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.services.email_input_assembler_service import EmailInputAssemblerService
from app.services.evidence_mapping_service import EvidenceMappingService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def test_evidence_links_created(session):
    _, candidate = make_phase7_ready_candidate(session)
    phase6 = session.query(Phase6CandidateDecision).filter_by(candidate_business_id=candidate.id).one()
    row = EmailInputAssemblerService(session, Settings()).assemble(1, candidate, phase6)
    links = EvidenceMappingService().links(1, row)
    assert links
    assert any(link.evidence_source_table == "future_email_offer_blocks" for link in links)
