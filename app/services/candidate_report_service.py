import csv
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.run_context import new_run_id
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_conflict import CandidateConflict
from app.db.models.candidate_manual_review_item import CandidateManualReviewItem
from app.db.models.candidate_personalization_evidence import CandidatePersonalizationEvidence
from app.db.models.candidate_source_link import CandidateSourceLink
from app.db.models.duplicate_cluster import DuplicateCluster
from app.db.models.normalization_run import NormalizationRun

PHASE3_WARNING = (
    "This phase does not verify website absence, authorize outreach, create send-ready leads, "
    "or generate email copy. Website missing evidence remains unverified until Phase 4. "
    "Raw email/phone data does not grant outreach permission."
)


class CandidateReportService:
    def __init__(self, session: Session):
        self.session = session

    def summary(self, run_id: str | None = None) -> dict[str, object]:
        candidates = self.session.scalars(select(CandidateBusiness)).all()
        reviews = self.session.scalars(select(CandidateManualReviewItem)).all()
        clusters = self.session.scalars(select(DuplicateCluster)).all()
        conflicts = self.session.scalars(select(CandidateConflict)).all()
        evidence = self.session.scalars(select(CandidatePersonalizationEvidence)).all()
        links = self.session.scalars(select(CandidateSourceLink)).all()
        runs = self.session.scalars(select(NormalizationRun)).all()
        ready = [
            item
            for item in candidates
            if item.status.value == "READY_FOR_WEBSITE_VERIFICATION"
        ]
        blocked = [
            item
            for item in candidates
            if item.status.value not in {"READY_FOR_WEBSITE_VERIFICATION"}
        ]
        verdict = (
            "PHASE_3_READY_WITH_MANUAL_REVIEW_GAPS"
            if reviews
            else "PHASE_3_CANDIDATE_NORMALIZATION_READY"
        )
        return {
            "warning": PHASE3_WARNING,
            "run_id": run_id or new_run_id(),
            "raw_records_processed": sum(run.input_raw_count for run in runs),
            "candidates_created_or_present": len(candidates),
            "source_links_count": len(links),
            "alias_count": sum(len(item.aliases) for item in candidates),
            "duplicate_clusters": len(clusters),
            "auto_merged_clusters": sum(
                1 for item in clusters if item.cluster_status.value == "AUTO_MERGED"
            ),
            "manual_review_clusters": sum(
                1 for item in clusters if item.cluster_status.value == "NEEDS_MANUAL_REVIEW"
            ),
            "manual_review_items": len(reviews),
            "conflict_count": len(conflicts),
            "chain_branch_risk_count": sum(1 for item in candidates if item.chain_risk_score >= 70),
            "generic_name_risk_count": sum(
                1 for item in candidates if item.generic_name_risk_score >= 80
            ),
            "candidates_ready_for_phase_4": len(ready),
            "candidates_blocked": len(blocked),
            "personalization_evidence_count": len(evidence),
            "final_verdict": verdict,
        }

    def write_candidate_report(self, reports_dir: Path) -> tuple[Path, Path, dict[str, object]]:
        report = self.summary()
        reports_dir.mkdir(parents=True, exist_ok=True)
        run_id = str(report["run_id"])
        md_path = reports_dir / f"candidate-businesses-{run_id}.md"
        json_path = reports_dir / f"candidate-businesses-{run_id}.json"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        lines = ["# Candidate Businesses", "", str(report["warning"]), ""]
        for key, value in report.items():
            if key != "warning":
                lines.append(f"- {key}: `{value}`")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return md_path, json_path, report

    def write_manual_review_report(self, reports_dir: Path) -> tuple[Path, Path]:
        run_id = new_run_id()
        reports_dir.mkdir(parents=True, exist_ok=True)
        rows = self.session.scalars(select(CandidateManualReviewItem)).all()
        md_path = reports_dir / f"manual-review-items-{run_id}.md"
        csv_path = reports_dir / f"manual-review-items-{run_id}.csv"
        md_path.write_text(
            "# Manual Review Items\n\n" + PHASE3_WARNING + "\n\n"
            + "\n".join(f"- {row.review_type.value}: {row.reason}" for row in rows)
            + "\n",
            encoding="utf-8",
        )
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["id", "review_type", "severity", "reason", "status"])
            for row in rows:
                writer.writerow(
                    [row.id, row.review_type.value, row.severity, row.reason, row.status.value]
                )
        return md_path, csv_path
