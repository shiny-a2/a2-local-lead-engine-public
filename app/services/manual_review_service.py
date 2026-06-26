import csv
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ManualReviewStatus, ManualReviewType
from app.db.models.candidate_manual_review_item import CandidateManualReviewItem


class ManualReviewService:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        review_type: ManualReviewType,
        reason: str,
        *,
        candidate_business_id: int | None = None,
        duplicate_cluster_id: int | None = None,
        severity: str = "medium",
        evidence: dict | None = None,
    ) -> CandidateManualReviewItem:
        item = CandidateManualReviewItem(
            candidate_business_id=candidate_business_id,
            duplicate_cluster_id=duplicate_cluster_id,
            review_type=review_type,
            severity=severity,
            reason=reason,
            evidence_json=evidence or {},
            status=ManualReviewStatus.OPEN,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def export(self, run_id: str, reports_dir: Path) -> tuple[Path, Path]:
        reports_dir.mkdir(parents=True, exist_ok=True)
        rows = self.session.scalars(select(CandidateManualReviewItem)).all()
        md_path = reports_dir / f"manual-review-items-{run_id}.md"
        csv_path = reports_dir / f"manual-review-items-{run_id}.csv"
        md_lines = [
            "# Manual Review Items",
            "",
            "This phase does not verify website absence, authorize outreach, create send-ready "
            "leads, or generate email copy.",
            "",
        ]
        for row in rows:
            md_lines.append(f"- {row.review_type.value}: {row.reason} ({row.status.value})")
        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["id", "review_type", "severity", "reason", "status"])
            for row in rows:
                writer.writerow(
                    [row.id, row.review_type.value, row.severity, row.reason, row.status.value]
                )
        return md_path, csv_path
