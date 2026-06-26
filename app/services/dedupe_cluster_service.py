from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    DuplicateClusterStatus,
    ManualReviewType,
    NormalizationOperation,
    NormalizationRunStatus,
)
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.duplicate_cluster import DuplicateCluster
from app.services.candidate_builder_service import CandidateBuilderService
from app.services.manual_review_service import ManualReviewService


class DedupeClusterService:
    def __init__(self, session: Session):
        self.session = session

    def run(self, campaign_slug: str | None, *, commit: bool) -> tuple[str, list[DuplicateCluster]]:
        builder = CandidateBuilderService(self.session)
        run = builder.start_run(
            NormalizationOperation.DEDUPE_CANDIDATES,
            campaign_slug=campaign_slug,
            dry_run=not commit,
        )
        candidates = self.session.scalars(select(CandidateBusiness)).all()
        groups: dict[str, list[CandidateBusiness]] = defaultdict(list)
        for candidate in candidates:
            groups[f"{candidate.normalized_name}:{candidate.canonical_category}"].append(candidate)
        clusters: list[DuplicateCluster] = []
        if not commit:
            run.status = NormalizationRunStatus.DRY_RUN_ONLY
            run.duplicate_cluster_count = sum(1 for group in groups.values() if len(group) > 1)
            run.finished_at = datetime.now(UTC)
            self.session.commit()
            return run.run_id, []
        review = ManualReviewService(self.session)
        for key, group in groups.items():
            if len(group) < 2:
                continue
            risk_flags = []
            if len({item.suburb for item in group if item.suburb}) > 1:
                risk_flags.append("multiple_suburbs_branch_risk")
            cluster_status = (
                DuplicateClusterStatus.NEEDS_MANUAL_REVIEW
                if risk_flags or max(item.chain_risk_score for item in group) >= 70
                else DuplicateClusterStatus.AUTO_MERGED
            )
            cluster = DuplicateCluster(
                normalization_run_id=run.id,
                cluster_key=key,
                cluster_status=cluster_status,
                candidate_business_id=group[0].id
                if cluster_status == DuplicateClusterStatus.AUTO_MERGED
                else None,
                raw_record_ids_json=[item.id for item in group],
                cluster_score=85 if cluster_status == DuplicateClusterStatus.AUTO_MERGED else 65,
                cluster_reasons_json=["same_normalized_name_and_category"],
                risk_flags_json=risk_flags,
            )
            self.session.add(cluster)
            self.session.flush()
            clusters.append(cluster)
            if cluster_status == DuplicateClusterStatus.NEEDS_MANUAL_REVIEW:
                review.create(
                    ManualReviewType.AMBIGUOUS_DUPLICATE,
                    "Duplicate cluster requires manual review before merge.",
                    duplicate_cluster_id=cluster.id,
                    evidence={
                        "candidate_ids": [item.id for item in group],
                        "risk_flags": risk_flags,
                    },
                )
                run.manual_review_count += 1
        run.duplicate_cluster_count = len(clusters)
        run.status = (
            NormalizationRunStatus.COMPLETED_WITH_WARNINGS
            if run.manual_review_count
            else NormalizationRunStatus.COMPLETED
        )
        run.finished_at = datetime.now(UTC)
        self.session.commit()
        return run.run_id, clusters
