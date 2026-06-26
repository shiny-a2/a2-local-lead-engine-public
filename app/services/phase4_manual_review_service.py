import csv
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.enums import ManualReviewStatus, Phase4ReviewType
from app.db.models.phase4_manual_review_item import Phase4ManualReviewItem


class Phase4ManualReviewService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, candidate_id: int, run_id: int, review_type: Phase4ReviewType, reason: str, severity: str = "medium") -> Phase4ManualReviewItem:
        row = Phase4ManualReviewItem(
            candidate_business_id=candidate_id,
            verification_run_id=run_id,
            review_type=review_type,
            severity=severity,
            reason=reason,
            recommended_action="Review evidence before Phase 5 scoring.",
            evidence_json={},
            status=ManualReviewStatus.OPEN,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def export_csv(self, rows: list[Phase4ManualReviewItem], path: Path) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["id", "candidate_business_id", "review_type", "severity", "reason", "status"])
            for row in rows:
                writer.writerow([row.id, row.candidate_business_id, row.review_type.value, row.severity, row.reason, row.status.value])

