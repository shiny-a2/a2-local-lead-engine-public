from app.core.enums import Phase5Decision
from app.services.offer_readiness_gate_service import OfferReadinessGateService


def test_missing_playbook_blocks():
    gates = OfferReadinessGateService().build(
        has_playbook=False,
        offer_fit_score=90,
        blocked_claim_count=0,
        email_block_count=1,
        selected_module_count=1,
        phase5_decision=Phase5Decision.READY_FOR_PHASE_6_INSIGHT,
        complex_module_count=0,
        price_ok=True,
    )
    assert any(not gate["passed"] for gate in gates)


def test_good_offer_gates_pass():
    gates = OfferReadinessGateService().build(
        has_playbook=True,
        offer_fit_score=90,
        blocked_claim_count=0,
        email_block_count=1,
        selected_module_count=1,
        phase5_decision=Phase5Decision.READY_FOR_PHASE_6_INSIGHT,
        complex_module_count=0,
        price_ok=True,
    )
    assert all(gate["passed"] for gate in gates)
