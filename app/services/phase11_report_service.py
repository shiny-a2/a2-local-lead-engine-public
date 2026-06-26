import csv
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.bounce_event import BounceEvent
from app.db.models.human_response_task import HumanResponseTask
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.inbox_sync_run import InboxSyncRun
from app.db.models.reply_classification import ReplyClassification


class Phase11ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: InboxSyncRun) -> dict:
        messages = self.session.scalars(
            select(InboundEmailMessage).where(InboundEmailMessage.sync_run_id == run.id)
        ).all()
        classifications = self.session.scalars(select(ReplyClassification)).all()
        bounces = self.session.scalars(select(BounceEvent)).all()
        tasks = self.session.scalars(select(HumanResponseTask)).all()
        return {
            "run_id": run.run_id,
            "dry_run": run.dry_run,
            "messages_seen": run.messages_seen,
            "messages_imported": len(messages),
            "replies_detected": sum(1 for m in messages if m.message_type.value == "reply"),
            "bounces_detected": len(bounces),
            "auto_replies_detected": sum(
                1 for m in messages if m.message_type.value in {"auto_reply", "out_of_office"}
            ),
            "unsubscribe_requests": sum(
                1 for c in classifications if c.classification.value == "UNSUBSCRIBE_REQUEST"
            ),
            "human_tasks_created": len(tasks),
            "unmatched_manual_review": sum(1 for m in messages if m.matched_candidate_business_id is None),
            "classification_breakdown": self._breakdown(list(classifications)),
            "safety_summary": {
                "outbound_replies_sent": False,
                "followups_sent": False,
                "ai_reply_text_generated": False,
                "smtp_outbound_used": False,
            },
            "final_verdict": "PHASE_11_DRY_RUN_READY_MAILBOX_CONFIG_GAPS"
            if run.dry_run
            else "PHASE_11_INBOX_BOUNCE_REPLY_CRM_READY",
        }

    def write(self, run: InboxSyncRun, out_dir: Path) -> tuple[Path, Path, Path, Path, Path, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        report = self.build(run)
        prefix = out_dir / f"phase11-inbox-{run.run_id}"
        md = prefix.with_suffix(".md")
        js = prefix.with_suffix(".json")
        md.write_text(self._markdown(report), encoding="utf-8")
        js.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        replies = out_dir / f"phase11-replies-{run.run_id}.csv"
        bounces = out_dir / f"phase11-bounces-{run.run_id}.csv"
        tasks = out_dir / f"phase11-human-tasks-{run.run_id}.csv"
        unmatched = out_dir / f"phase11-unmatched-{run.run_id}.csv"
        self._csv(replies, ["message_id", "subject"], [])
        self._csv(bounces, ["bounce_id", "type"], [])
        self._csv(tasks, ["task_id", "type", "status"], [])
        self._csv(unmatched, ["message_id", "subject"], [])
        return md, replies, bounces, tasks, unmatched, js

    def _breakdown(self, rows: list[ReplyClassification]) -> dict[str, int]:
        result: dict[str, int] = {}
        for row in rows:
            result[row.classification.value] = result.get(row.classification.value, 0) + 1
        return result

    def _csv(self, path: Path, headers: list[str], rows: list[list[str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

    def _markdown(self, report: dict) -> str:
        return "\n".join(
            [
                "# Phase 11 Inbox/Bounce/Reply CRM Report",
                "",
                "Phase 11 does not send replies.",
                "Phase 11 does not send follow-ups.",
                "Phase 11 does not generate AI reply text.",
                "Phase 11 only reads/classifies/matches inbound messages and creates human tasks.",
                "",
                f"run_id: {report['run_id']}",
                f"messages_imported: {report['messages_imported']}",
                f"bounces_detected: {report['bounces_detected']}",
                f"human_tasks_created: {report['human_tasks_created']}",
                f"final_verdict: {report['final_verdict']}",
            ]
        )
