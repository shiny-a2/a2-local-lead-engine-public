import csv
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.models.human_review_run import HumanReviewRun


class ReviewPackExportService:
    def __init__(self, session: Session):
        self.session = session

    def export(self, run: HumanReviewRun, reports_dir: Path) -> tuple[Path, Path, Path]:
        reports_dir.mkdir(exist_ok=True)
        rows = self.session.scalars(
            select(HumanReviewQueueItem).where(HumanReviewQueueItem.human_review_run_id == run.id)
        ).all()
        md = reports_dir / f"phase9-human-review-queue-{run.run_id}.md"
        csv_path = reports_dir / f"phase9-review-items-{run.run_id}.csv"
        json_path = reports_dir / f"phase9-review-details-{run.run_id}.json"
        md.write_text(
            "\n".join(
                [
                    "# Phase 9 Human Review Queue",
                    "",
                    "Phase 9 does not send, schedule, sync inboxes, or process bounces.",
                    f"- run_id: {run.run_id}",
                    f"- queue_items: {len(rows)}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["queue_item_id", "candidate_business_id", "draft_id", "status", "campaign_lane"])
            for row in rows:
                writer.writerow([row.id, row.candidate_business_id, row.email_draft_variant_id, row.queue_status.value, row.campaign_lane])
        json_path.write_text(
            json.dumps(
                {
                    "run_id": run.run_id,
                    "queue_items_count": len(rows),
                    "items": [
                        {
                            "queue_item_id": row.id,
                            "candidate_business_id": row.candidate_business_id,
                            "draft_id": row.email_draft_variant_id,
                            "status": row.queue_status.value,
                        }
                        for row in rows
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return md, csv_path, json_path
