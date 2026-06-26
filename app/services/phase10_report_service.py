import csv
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.email_send_attempt import EmailSendAttempt
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.send_queue_run import SendQueueRun


class Phase10ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: SendQueueRun) -> dict[str, object]:
        items = self.session.scalars(select(EmailSendQueue).where(EmailSendQueue.send_queue_run_id == run.id)).all()
        attempts = self.session.scalars(select(EmailSendAttempt)).all()
        statuses = Counter(item.queue_status.value for item in items)
        verdict = "PHASE_10_DRY_RUN_READY_NO_SEND_EXECUTED" if run.dry_run else "PHASE_10_CONTROLLED_SENDING_READY"
        if run.blocked_count:
            verdict = "PHASE_10_READY_WITH_SEND_BLOCKERS"
        if run.status.value == "BLOCKED_BY_GLOBAL_KILL_SWITCH":
            verdict = "PHASE_10_BLOCKED_BY_GLOBAL_KILL_SWITCH"
        return {
            "run_id": run.run_id,
            "provider": "cpanel_smtp",
            "dry_run": run.dry_run,
            "input_approved_count": run.input_approved_count,
            "queued_count": run.queued_count,
            "blocked_count": run.blocked_count,
            "sent_to_provider_count": statuses["SENT_TO_PROVIDER"],
            "failed_count": run.failed_count,
            "suppression_blocks": statuses["BLOCKED_BY_SUPPRESSION"],
            "duplicate_send_blocks": statuses["BLOCKED_DUPLICATE_SEND"],
            "global_kill_switch_blocks": statuses["BLOCKED_BY_GLOBAL_KILL_SWITCH"],
            "provider_circuit_breaker_blocks": statuses["BLOCKED_BY_PROVIDER_CIRCUIT_BREAKER"],
            "send_window_blocks": statuses["BLOCKED_BY_SEND_WINDOW"],
            "provider_errors": [a.error_type for a in attempts if a.error_type],
            "cpanel_delivery_unknown_count": statuses["SENT_TO_PROVIDER"],
            "safety_summary": {
                "bulk_blast": False,
                "followup_automation": False,
                "inbox_sync": False,
                "bounce_parsing": False,
                "tracking_pixel": False,
                "click_tracking": False,
            },
            "warnings": [
                "Phase 10 handles controlled sending only.",
                "Follow-up automation is not implemented.",
                "Inbox/reply processing is not implemented.",
                "Bounce parsing is not implemented.",
                "cPanel SMTP acceptance does not guarantee inbox delivery.",
            ],
            "final_verdict": verdict,
        }

    def write(self, run: SendQueueRun, reports_dir: Path) -> tuple[Path, Path, Path, Path, Path, Path, dict[str, object]]:
        reports_dir.mkdir(exist_ok=True)
        report = self.build(run)
        md = reports_dir / f"phase10-send-{run.run_id}.md"
        json_path = reports_dir / f"phase10-send-{run.run_id}.json"
        sent = reports_dir / f"phase10-sent-{run.run_id}.csv"
        blocked = reports_dir / f"phase10-blocked-{run.run_id}.csv"
        errors = reports_dir / f"phase10-provider-errors-{run.run_id}.csv"
        plan = reports_dir / f"phase10-send-plan-{run.run_id}.csv"
        md.write_text(self._markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        for path, mode in [(sent, "sent"), (blocked, "blocked"), (plan, "plan")]:
            self._write_items(run, path, mode)
        self._write_errors(errors)
        return md, json_path, sent, blocked, errors, plan, report

    def _markdown(self, report: dict[str, object]) -> str:
        return "\n".join(["# Phase 10 Controlled Send Report", "", "cPanel SMTP acceptance does not guarantee inbox delivery.", f"- run_id: {report['run_id']}", f"- sent_to_provider_count: {report['sent_to_provider_count']}", f"- blocked_count: {report['blocked_count']}", f"- final_verdict: {report['final_verdict']}", ""])

    def _write_items(self, run: SendQueueRun, path: Path, mode: str) -> None:
        rows = self.session.scalars(select(EmailSendQueue).where(EmailSendQueue.send_queue_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["queue_id", "recipient", "status"])
            for row in rows:
                if mode == "sent" and row.queue_status.value != "SENT_TO_PROVIDER":
                    continue
                if mode == "blocked" and "BLOCKED" not in row.queue_status.value:
                    continue
                writer.writerow([row.id, row.recipient_email, row.queue_status.value])

    def _write_errors(self, path: Path) -> None:
        rows = self.session.scalars(select(EmailSendAttempt).where(EmailSendAttempt.error_type.is_not(None))).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["queue_id", "error_type", "error_message"])
            for row in rows:
                writer.writerow([row.email_send_queue_id, row.error_type, row.error_message])
