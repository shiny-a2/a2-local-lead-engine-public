from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from app.core.enums import (
    ChecklistItemStatus,
    HumanApprovalType,
    ManualCommunicationChannel,
    ManualCommunicationType,
    OpportunityCloseReason,
    ProposalChecklistItemStatus,
)
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.proposal_checklist_item import ProposalChecklistItem
from app.db.models.scope_checklist_item import ScopeChecklistItem
from app.db.session import make_session_factory
from app.services.human_approval_ledger_service import HumanApprovalLedgerService
from app.services.internal_pricing_worksheet_service import InternalPricingWorksheetService
from app.services.manual_communication_log_service import ManualCommunicationLogService
from app.services.opportunity_close_service import OpportunityCloseService
from app.services.phase13_report_service import Phase13ReportService
from app.services.proposal_checklist_service import ProposalChecklistService
from app.services.proposal_readiness_gate_service import ProposalReadinessGateService
from app.services.quote_readiness_gate_service import QuoteReadinessGateService
from app.services.sales_workspace_service import SalesWorkspaceService
from app.services.scope_checklist_service import ScopeChecklistService
from app.services.scope_completeness_service import ScopeCompletenessService
from app.settings import get_settings

sales_workspace_app = typer.Typer(no_args_is_help=True)
console = Console()


def _session():
    return make_session_factory(get_settings())()


def _commit_mode(dry_run: bool, commit: bool) -> bool:
    if dry_run == commit:
        raise typer.BadParameter("Use exactly one of --dry-run or --commit.")
    return commit


@sales_workspace_app.command("build")
def build(
    campaign: Annotated[str, typer.Option()],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    live = _commit_mode(dry_run, commit)
    with _session() as session:
        summary = SalesWorkspaceService(session, get_settings()).build_for_campaign(campaign, live)
        if live:
            session.commit()
    for key, value in summary.items():
        console.print(f"{key}={value}")
    console.print("outbound_actions=false")


@sales_workspace_app.command("explain")
def explain(opportunity_id: Annotated[int, typer.Option()]) -> None:
    with _session() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity is None:
            raise typer.BadParameter("opportunity not found")
        console.print(f"opportunity_status={opportunity.opportunity_status.value}")
        console.print(f"opportunity_type={opportunity.opportunity_type.value}")
        console.print("next_step=human-only sales workspace")
        console.print("outbound_actions=false")


@sales_workspace_app.command("create-scope-checklist")
def create_scope_checklist(
    opportunity_id: Annotated[int, typer.Option()],
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    if not commit:
        raise typer.BadParameter("--commit required")
    with _session() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity is None:
            raise typer.BadParameter("opportunity not found")
        checklist = ScopeChecklistService(session).create_for_opportunity(opportunity)
        ScopeCompletenessService(session, get_settings()).calculate(checklist)
        session.commit()
    console.print("scope_checklist_created=true")


@sales_workspace_app.command("create-proposal-checklist")
def create_proposal_checklist(
    opportunity_id: Annotated[int, typer.Option()],
    commit: Annotated[bool, typer.Option("--commit")] = False,
) -> None:
    if not commit:
        raise typer.BadParameter("--commit required")
    with _session() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity is None:
            raise typer.BadParameter("opportunity not found")
        checklist = ProposalChecklistService(session).create_for_opportunity(opportunity)
        ProposalReadinessGateService(session, get_settings()).evaluate(checklist)
        session.commit()
    console.print("proposal_checklist_created=true")


@sales_workspace_app.command("update-scope-item")
def update_scope_item(
    item_id: Annotated[int, typer.Option()],
    answer: Annotated[str, typer.Option()] = "",
    status: Annotated[str, typer.Option()] = "ANSWERED",
) -> None:
    with _session() as session:
        item = session.get(ScopeChecklistItem, item_id)
        if item is None:
            raise typer.BadParameter("scope item not found")
        item.answer_text = answer
        item.status = ChecklistItemStatus(status)
        from app.db.models.scope_checklist import ScopeChecklist

        checklist = session.get(ScopeChecklist, item.scope_checklist_id)
        if checklist:
            ScopeCompletenessService(session, get_settings()).calculate(checklist)
        session.commit()
    console.print("scope_item_updated=true")


@sales_workspace_app.command("update-proposal-item")
def update_proposal_item(
    item_id: Annotated[int, typer.Option()],
    status: Annotated[str, typer.Option()],
    notes: Annotated[str, typer.Option()] = "",
) -> None:
    with _session() as session:
        item = session.get(ProposalChecklistItem, item_id)
        if item is None:
            raise typer.BadParameter("proposal item not found")
        item.status = ProposalChecklistItemStatus(status)
        item.notes = notes
        session.commit()
    console.print("proposal_item_updated=true")


@sales_workspace_app.command("update-pricing")
def update_pricing(
    opportunity_id: Annotated[int, typer.Option()],
    manual_base_price: Annotated[float, typer.Option()],
    notes: Annotated[str, typer.Option()] = "",
) -> None:
    with _session() as session:
        InternalPricingWorksheetService(session).update_manual_price(
            opportunity_id, manual_base_price, notes
        )
        QuoteReadinessGateService(session).evaluate(opportunity_id)
        session.commit()
    console.print("manual_pricing_updated=true")
    console.print("customer_facing_quote_created=false")


@sales_workspace_app.command("approve-quote-manually")
def approve_quote_manually(
    opportunity_id: Annotated[int, typer.Option()],
    approved_by: Annotated[str, typer.Option()],
    notes: Annotated[str, typer.Option()] = "",
) -> None:
    with _session() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity is None:
            raise typer.BadParameter("opportunity not found")
        InternalPricingWorksheetService(session).approve_manually(
            opportunity_id, approved_by, notes
        )
        HumanApprovalLedgerService(session).record(
            opportunity, HumanApprovalType.MANUAL_QUOTE_APPROVAL, approved_by, notes
        )
        QuoteReadinessGateService(session).evaluate(opportunity_id)
        session.commit()
    console.print("quote_approved_manually=true")
    console.print("quote_sent_by_system=false")


@sales_workspace_app.command("log-manual-communication")
def log_manual_communication(
    opportunity_id: Annotated[int, typer.Option()],
    type: Annotated[str, typer.Option()],
    summary: Annotated[str, typer.Option()],
    created_by: Annotated[str, typer.Option()] = "Amirali",
) -> None:
    with _session() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity is None:
            raise typer.BadParameter("opportunity not found")
        ManualCommunicationLogService(session).log(
            opportunity,
            ManualCommunicationType(type),
            summary,
            created_by,
            ManualCommunicationChannel.MANUAL_NOTE,
        )
        session.commit()
    console.print("manual_communication_logged=true")
    console.print("system_performed_outbound_action=false")


@sales_workspace_app.command("close")
def close(
    opportunity_id: Annotated[int, typer.Option()],
    reason: Annotated[str, typer.Option()],
    closed_by: Annotated[str, typer.Option()],
    notes: Annotated[str, typer.Option()] = "",
) -> None:
    with _session() as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity is None:
            raise typer.BadParameter("opportunity not found")
        OpportunityCloseService(session).close(
            opportunity, OpportunityCloseReason(reason), closed_by, notes
        )
        session.commit()
    console.print("closed=true")


def report_sales_workspace(campaign: str = "") -> None:
    with _session() as session:
        paths = Phase13ReportService(session).write(Path("reports"))
    console.print(f"markdown={paths[0]}")
    console.print(f"json={paths[1]}")
    console.print(f"open_csv={paths[2]}")
    console.print(f"scope_gaps_csv={paths[3]}")
    console.print(f"proposal_csv={paths[4]}")
    console.print(f"tasks_csv={paths[5]}")
    console.print("outbound_actions=false")
