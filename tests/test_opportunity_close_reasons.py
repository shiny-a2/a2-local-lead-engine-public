import pytest

from app.core.enums import OpportunityCloseReason
from app.db.models.phase13_audit_event import Phase13AuditEvent
from app.services.opportunity_close_service import OpportunityCloseService
from tests.phase12_helpers import build_opportunity_from_body


def test_close_reason_required(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    with pytest.raises(ValueError):
        OpportunityCloseService(session).close(opportunity, None, "Amirali")  # type: ignore[arg-type]


def test_closed_opportunities_excluded_from_active_board(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    OpportunityCloseService(session).close(opportunity, OpportunityCloseReason.NO_RESPONSE, "Amirali")
    assert opportunity.opportunity_status.name.startswith("CLOSED")


def test_close_audit_event_created(session):
    _, _, _, opportunity = build_opportunity_from_body(session, "yes interested")
    OpportunityCloseService(session).close(opportunity, OpportunityCloseReason.NO_RESPONSE, "Amirali")
    assert session.query(Phase13AuditEvent).count() >= 1
