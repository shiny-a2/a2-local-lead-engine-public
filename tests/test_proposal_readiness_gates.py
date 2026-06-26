from app.services.proposal_checklist_service import ProposalChecklistService
from app.services.proposal_readiness_gate_service import ProposalReadinessGateService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_missing_package_blocks_proposal_readiness(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "send details please")
    checklist = ProposalChecklistService(session).create_for_opportunity(opportunity)
    gates = ProposalReadinessGateService(session, Settings(testing=True)).evaluate(checklist)
    assert any(gate.gate_name.value == "recommended_package_gate" and not gate.passed for gate in gates)


def test_missing_exclusions_client_responsibilities_blocks_readiness(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "send details please")
    checklist = ProposalChecklistService(session).create_for_opportunity(opportunity)
    gates = ProposalReadinessGateService(session, Settings(testing=True)).evaluate(checklist)
    blocked = {gate.gate_name.value for gate in gates if not gate.passed}
    assert "excluded_items_gate" in blocked
    assert "client_responsibilities_gate" in blocked


def test_human_proposal_approval_required(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "send details please")
    checklist = ProposalChecklistService(session).create_for_opportunity(opportunity)
    gates = ProposalReadinessGateService(session, Settings(testing=True)).evaluate(checklist)
    assert any(gate.gate_name.value == "human_proposal_approval_gate" and not gate.passed for gate in gates)
