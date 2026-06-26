from sqlalchemy import select

from app.core.enums import ProposalChecklistItemStatus
from app.db.models.proposal_checklist_item import ProposalChecklistItem
from app.services.proposal_checklist_service import ProposalChecklistService
from app.services.proposal_readiness_gate_service import ProposalReadinessGateService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_proposal_checklist_created(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "send details please")
    checklist = ProposalChecklistService(session).create_for_opportunity(opportunity)
    assert checklist.id is not None


def test_missing_items_detected(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "send details please")
    checklist = ProposalChecklistService(session).create_for_opportunity(opportunity)
    gates = ProposalReadinessGateService(session, Settings(testing=True)).evaluate(checklist)
    assert any(not gate.passed for gate in gates)


def test_ready_state_works_without_customer_proposal(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "send details please")
    checklist = ProposalChecklistService(session).create_for_opportunity(opportunity)
    items = session.scalars(select(ProposalChecklistItem).where(ProposalChecklistItem.proposal_checklist_id == checklist.id)).all()
    for item in items:
        item.status = ProposalChecklistItemStatus.READY
    ProposalReadinessGateService(session, Settings(testing=True)).evaluate(checklist)
    assert checklist.status.value == "READY_FOR_HUMAN_REVIEW"
    assert not hasattr(checklist, "customer_facing_proposal")
