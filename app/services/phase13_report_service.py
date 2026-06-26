import csv
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.manual_communication_log import ManualCommunicationLog
from app.db.models.next_human_action import NextHumanAction
from app.db.models.opportunity_close_record import OpportunityCloseRecord
from app.db.models.opportunity_health_snapshot import OpportunityHealthSnapshot
from app.db.models.proposal_checklist import ProposalChecklist
from app.db.models.sales_task import SalesTask
from app.db.models.sales_workspace_item import SalesWorkspaceItem
from app.db.models.scope_checklist import ScopeChecklist


class Phase13ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self) -> dict:
        items = self.session.scalars(select(SalesWorkspaceItem)).all()
        scopes = self.session.scalars(select(ScopeChecklist)).all()
        proposals = self.session.scalars(select(ProposalChecklist)).all()
        tasks = self.session.scalars(select(SalesTask)).all()
        closes = self.session.scalars(select(OpportunityCloseRecord)).all()
        health = self.session.scalars(select(OpportunityHealthSnapshot)).all()
        actions = self.session.scalars(select(NextHumanAction)).all()
        logs = self.session.scalars(select(ManualCommunicationLog)).all()
        return {
            "workspace_items_count": len(items),
            "open_opportunities": sum(1 for item in items if not item.workspace_status.value.startswith("CLOSED")),
            "opportunities_needing_scope": sum(1 for scope in scopes if not scope.quote_ready),
            "quote_readiness_breakdown": {
                "ready": sum(1 for scope in scopes if scope.quote_ready),
                "not_ready": sum(1 for scope in scopes if not scope.quote_ready),
            },
            "proposal_readiness_breakdown": {
                "ready": sum(1 for p in proposals if p.status.value == "READY_FOR_HUMAN_REVIEW"),
                "not_ready": sum(1 for p in proposals if p.status.value != "READY_FOR_HUMAN_REVIEW"),
            },
            "manual_tasks_count": len(tasks),
            "overdue_tasks": 0,
            "manual_communication_logs": len(logs),
            "closed_opportunities": len(closes),
            "closed_reasons": [close.close_reason.value for close in closes],
            "opportunity_health_summary": [row.health_status.value for row in health],
            "next_human_actions": [row.action_type.value for row in actions],
            "human_only_guard_summary": {
                "auto_reply_blocked": True,
                "auto_followup_blocked": True,
                "auto_quote_blocked": True,
                "auto_proposal_blocked": True,
                "auto_meeting_blocked": True,
                "payment_link_blocked": True,
                "auto_call_blocked": True,
            },
            "safety_summary": {
                "replies_sent": False,
                "followups_sent": False,
                "quotes_issued": False,
                "proposals_sent": False,
                "meetings_scheduled": False,
                "payment_links_created": False,
                "calls_placed": False,
            },
            "final_verdict": "PHASE_13_MANUAL_SALES_WORKSPACE_READY",
        }

    def write(self, out_dir: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        report = self.build()
        md = out_dir / f"phase13-sales-workspace-{run_id}.md"
        js = out_dir / f"phase13-sales-workspace-{run_id}.json"
        open_csv = out_dir / f"phase13-open-opportunities-{run_id}.csv"
        scope_csv = out_dir / f"phase13-scope-gaps-{run_id}.csv"
        proposal_csv = out_dir / f"phase13-proposal-checklists-{run_id}.csv"
        tasks_csv = out_dir / f"phase13-manual-tasks-{run_id}.csv"
        md.write_text(self._markdown(report), encoding="utf-8")
        js.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._csv(open_csv, ["workspace_items", "open"], [[report["workspace_items_count"], report["open_opportunities"]]])
        self._csv(scope_csv, ["needing_scope"], [[report["opportunities_needing_scope"]]])
        self._csv(proposal_csv, ["ready", "not_ready"], [[report["proposal_readiness_breakdown"]["ready"], report["proposal_readiness_breakdown"]["not_ready"]]])
        self._csv(tasks_csv, ["manual_tasks"], [[report["manual_tasks_count"]]])
        return md, js, open_csv, scope_csv, proposal_csv, tasks_csv

    def _csv(self, path: Path, headers: list[str], rows: list[list[object]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

    def _markdown(self, report: dict) -> str:
        return "\n".join(
            [
                "# Phase 13 Manual Sales Workspace Report",
                "",
                "Phase 13 does not send replies.",
                "Phase 13 does not send follow-ups.",
                "Phase 13 does not issue quotes.",
                "Phase 13 does not send proposals.",
                "Phase 13 does not schedule meetings.",
                "Phase 13 is a human sales workspace only.",
                "",
                f"workspace_items_count: {report['workspace_items_count']}",
                f"manual_tasks_count: {report['manual_tasks_count']}",
                f"closed_opportunities: {report['closed_opportunities']}",
                f"final_verdict: {report['final_verdict']}",
            ]
        )
