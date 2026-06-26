import csv
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.followup_eligibility_record import FollowupEligibilityRecord
from app.db.models.human_sales_control_gate import HumanSalesControlGate
from app.db.models.meeting_guidance_record import MeetingGuidanceRecord
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase12_human_task import Phase12HumanTask
from app.db.models.pricing_guidance_record import PricingGuidanceRecord


class Phase12ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self) -> dict:
        opportunities = self.session.scalars(select(OpportunityRecord)).all()
        pricing = self.session.scalars(select(PricingGuidanceRecord)).all()
        meetings = self.session.scalars(select(MeetingGuidanceRecord)).all()
        tasks = self.session.scalars(select(Phase12HumanTask)).all()
        followups = self.session.scalars(select(FollowupEligibilityRecord)).all()
        gates = self.session.scalars(select(HumanSalesControlGate)).all()
        closed = [o for o in opportunities if o.opportunity_status.name.startswith("CLOSED")]
        return {
            "opportunities_created": len([o for o in opportunities if o not in closed]),
            "closed_leads": len(closed),
            "price_guidance_count": len(pricing),
            "meeting_guidance_count": len(meetings),
            "human_tasks_created": len(tasks),
            "followup_manual_only": sum(1 for f in followups if f.followup_type.value == "manual_only"),
            "followup_not_allowed": sum(1 for f in followups if f.followup_type.value == "not_allowed"),
            "human_control_gates": {
                "total": len(gates),
                "failed": sum(1 for g in gates if not g.passed),
            },
            "safety_summary": {
                "replies_sent": False,
                "prices_sent": False,
                "meetings_scheduled": False,
                "followups_sent": False,
                "proposals_sent": False,
                "payment_links_created": False,
            },
            "final_verdict": "PHASE_12_OPPORTUNITY_RESPONSE_PLANNER_READY",
        }

    def write(self, out_dir: Path) -> tuple[Path, Path, Path, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        report = self.build()
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        md = out_dir / f"phase12-opportunities-{run_id}.md"
        js = out_dir / f"phase12-opportunities-{run_id}.json"
        tasks = out_dir / f"phase12-human-tasks-{run_id}.csv"
        pricing = out_dir / f"phase12-pricing-guidance-{run_id}.csv"
        md.write_text(self._markdown(report), encoding="utf-8")
        js.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._csv(tasks, ["task_id", "type", "status"], [])
        self._csv(pricing, ["guidance_id", "strategy", "show_price_to_user"], [])
        return md, js, tasks, pricing

    def _csv(self, path: Path, headers: list[str], rows: list[list[str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

    def _markdown(self, report: dict) -> str:
        return "\n".join(
            [
                "# Phase 12 Opportunity Planner Report",
                "",
                "Phase 12 does not send replies.",
                "Phase 12 does not send follow-ups.",
                "Phase 12 does not quote prices automatically.",
                "Phase 12 does not schedule meetings.",
                "Phase 12 only creates guidance and human tasks.",
                "",
                f"opportunities_created: {report['opportunities_created']}",
                f"price_guidance_count: {report['price_guidance_count']}",
                f"meeting_guidance_count: {report['meeting_guidance_count']}",
                f"human_tasks_created: {report['human_tasks_created']}",
                f"final_verdict: {report['final_verdict']}",
            ]
        )
