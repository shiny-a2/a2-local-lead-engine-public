import csv
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import HumanReviewQueueStatus
from app.db.models.final_pre_send_check import FinalPreSendCheck
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.models.human_review_run import HumanReviewRun
from app.db.models.phase9_candidate_decision import Phase9CandidateDecision


class Phase9ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: HumanReviewRun) -> dict[str, object]:
        items = self.session.scalars(select(HumanReviewQueueItem).where(HumanReviewQueueItem.human_review_run_id == run.id)).all()
        checks = self.session.scalars(select(FinalPreSendCheck)).all()
        decisions = self.session.scalars(select(Phase9CandidateDecision).where(Phase9CandidateDecision.human_review_run_id == run.id)).all()
        statuses = Counter(item.queue_status.value for item in items)
        blocked = statuses[HumanReviewQueueStatus.BLOCKED_BY_FINAL_PRE_SEND_CHECK.value]
        ready = sum(1 for row in decisions if row.ready_for_phase10)
        verdict = "PHASE_9_HUMAN_APPROVAL_QUEUE_READY"
        if blocked:
            verdict = "PHASE_9_BLOCKED_BY_FINAL_PRE_SEND_CHECKS"
        elif any("mailbox_readiness_future_phase" in (check.risk_flags_json or []) for check in checks):
            verdict = "PHASE_9_DASHBOARD_READY_WITH_SENDER_CONFIG_GAPS"
        return {
            "run_id": run.run_id,
            "queue_items_count": len(items),
            "approved_for_phase10_count": ready,
            "approved_with_warnings_count": statuses[HumanReviewQueueStatus.APPROVED_WITH_WARNINGS_FOR_PHASE10.value],
            "edit_required_count": statuses[HumanReviewQueueStatus.EDIT_REQUIRED.value],
            "returned_to_phase7_count": statuses[HumanReviewQueueStatus.RETURNED_TO_PHASE7_REWRITE.value],
            "returned_to_phase8_count": statuses[HumanReviewQueueStatus.RETURNED_TO_PHASE8_REJUDGE.value],
            "held_count": statuses[HumanReviewQueueStatus.HELD.value],
            "rejected_count": statuses[HumanReviewQueueStatus.REJECTED.value],
            "blocked_by_final_check_count": blocked,
            "suppression_failures": sum(1 for check in checks if not check.suppression_ok),
            "sender_readiness_summary": {"missing_sender_identity": sum(1 for check in checks if not check.sender_identity_ok)},
            "mailbox_readiness_summary": {"future_phase_warnings": sum(1 for check in checks if "mailbox_readiness_future_phase" in (check.risk_flags_json or []))},
            "manual_edit_count": 0,
            "rejudge_required_count": statuses[HumanReviewQueueStatus.REJUDGE_REQUIRED.value],
            "warnings": [
                "Phase 9 does not send emails.",
                "Phase 9 does not schedule emails.",
                "Phase 9 does not sync inboxes.",
                "Phase 9 does not process bounces.",
                "Phase 9 only prepares drafts for Phase 10 controlled sending.",
            ],
            "final_verdict": verdict,
        }

    def write(self, run: HumanReviewRun, reports_dir: Path) -> tuple[Path, Path, Path, Path, dict[str, object]]:
        reports_dir.mkdir(exist_ok=True)
        report = self.build(run)
        md = reports_dir / f"phase9-human-review-{run.run_id}.md"
        approved = reports_dir / f"phase9-approved-for-phase10-{run.run_id}.csv"
        blocked = reports_dir / f"phase9-blocked-{run.run_id}.csv"
        returned = reports_dir / f"phase9-returned-{run.run_id}.csv"
        json_path = reports_dir / f"phase9-human-review-{run.run_id}.json"
        md.write_text(self._markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._write_csv(run, approved, "approved")
        self._write_csv(run, blocked, "blocked")
        self._write_csv(run, returned, "returned")
        return md, approved, blocked, returned, report

    def _markdown(self, report: dict[str, object]) -> str:
        return "\n".join(
            [
                "# Phase 9 Human Review Report",
                "",
                "Phase 9 does not send, schedule, sync inboxes, or process bounces.",
                f"- run_id: {report['run_id']}",
                f"- queue_items_count: {report['queue_items_count']}",
                f"- approved_for_phase10_count: {report['approved_for_phase10_count']}",
                f"- blocked_by_final_check_count: {report['blocked_by_final_check_count']}",
                f"- final_verdict: {report['final_verdict']}",
                "",
            ]
        )

    def _write_csv(self, run: HumanReviewRun, path: Path, mode: str) -> None:
        items = self.session.scalars(select(HumanReviewQueueItem).where(HumanReviewQueueItem.human_review_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["queue_item_id", "candidate_business_id", "draft_id", "status"])
            for item in items:
                status = item.queue_status.value
                if mode == "approved" and "APPROVED" not in status:
                    continue
                if mode == "blocked" and "BLOCKED" not in status:
                    continue
                if mode == "returned" and "RETURNED" not in status:
                    continue
                writer.writerow([item.id, item.candidate_business_id, item.email_draft_variant_id, status])
