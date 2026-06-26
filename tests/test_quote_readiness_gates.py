from app.core.enums import HumanApprovalType
from app.services.human_approval_ledger_service import HumanApprovalLedgerService
from app.services.internal_pricing_worksheet_service import InternalPricingWorksheetService
from app.services.quote_readiness_gate_service import QuoteReadinessGateService
from tests.phase12_helpers import build_opportunity_from_body


def test_no_manual_price_blocks_quote_approval(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "what is the price?")
    InternalPricingWorksheetService(session).create_for_opportunity(opportunity)
    gates = QuoteReadinessGateService(session).evaluate(opportunity.id)
    assert any(not gate.passed and gate.gate_name.value == "manual_price_input_gate" for gate in gates)


def test_no_human_approval_blocks_final_quote_status(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "what is the price?")
    service = InternalPricingWorksheetService(session)
    service.create_for_opportunity(opportunity)
    service.update_manual_price(opportunity.id, 1200, "manual")
    gates = QuoteReadinessGateService(session).evaluate(opportunity.id)
    assert any(not gate.passed and gate.gate_name.value == "human_quote_approval_gate" for gate in gates)


def test_manual_input_and_approval_recorded(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "what is the price?")
    service = InternalPricingWorksheetService(session)
    service.create_for_opportunity(opportunity)
    service.update_manual_price(opportunity.id, 1200, "manual")
    service.approve_manually(opportunity.id, "Amirali")
    HumanApprovalLedgerService(session).record(opportunity, HumanApprovalType.MANUAL_QUOTE_APPROVAL, "Amirali")
    gates = QuoteReadinessGateService(session).evaluate(opportunity.id)
    assert any(gate.gate_name.value == "human_quote_approval_gate" and gate.passed for gate in gates)
