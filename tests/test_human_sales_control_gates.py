from app.core.enums import HumanSalesGateName
from app.db.models.human_sales_control_gate import HumanSalesControlGate
from tests.phase12_helpers import build_opportunity_from_body


def test_human_sales_gates_created(session):
    build_opportunity_from_body(session, "yes interested")
    names = {gate.gate_name for gate in session.query(HumanSalesControlGate).all()}
    assert HumanSalesGateName.NO_AUTO_PRICE_GATE in names
    assert HumanSalesGateName.NO_AUTO_MEETING_GATE in names
    assert HumanSalesGateName.NO_AUTO_REPLY_GATE in names
    assert HumanSalesGateName.NO_AUTO_PROPOSAL_GATE in names
    assert HumanSalesGateName.NO_AUTO_PAYMENT_LINK_GATE in names
