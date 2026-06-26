from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_manual_review_item import CandidateManualReviewItem
from app.db.models.duplicate_cluster import DuplicateCluster
from app.db.models.normalization_run import NormalizationRun
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


def _session():
    return make_session_factory(get_settings())()


@router.get("/candidate-businesses")
def candidate_businesses() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(CandidateBusiness).order_by(CandidateBusiness.id)).all()
        return [
            {
                "id": row.id,
                "display_name": row.display_name,
                "canonical_category": row.canonical_category,
                "city": row.city,
                "suburb": row.suburb,
                "status": row.status.value,
                "verification_readiness_status": row.verification_readiness_status.value,
            }
            for row in rows
        ]


@router.get("/candidate-businesses/{candidate_id}")
def candidate_business(candidate_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.get(CandidateBusiness, candidate_id)
        if row is None:
            return {"found": False}
        return {
            "found": True,
            "id": row.id,
            "display_name": row.display_name,
            "normalized_name": row.normalized_name,
            "candidate_identity_fingerprint": row.candidate_identity_fingerprint,
            "status": row.status.value,
        }


@router.get("/candidate-businesses/{candidate_id}/sources")
def candidate_sources(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        row = session.get(CandidateBusiness, candidate_id)
        if row is None:
            return []
        return [
            {
                "raw_source_record_id": link.raw_source_record_id,
                "source_name": link.source_name.value,
                "link_type": link.link_type.value,
                "match_score": link.match_score,
            }
            for link in row.source_links
        ]


@router.get("/candidate-businesses/{candidate_id}/quality")
def candidate_quality(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        row = session.get(CandidateBusiness, candidate_id)
        if row is None:
            return []
        return [
            {
                "quality_score": item.quality_score,
                "readiness_decision": item.readiness_decision.value,
                "quality_notes": item.quality_notes_json,
            }
            for item in row.quality_reports
        ]


@router.get("/candidate-businesses/{candidate_id}/evidence")
def candidate_evidence(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        row = session.get(CandidateBusiness, candidate_id)
        if row is None:
            return []
        return [
            {
                "evidence_type": item.evidence_type,
                "evidence_source": item.evidence_source,
                "allowed_for_future_copy": item.allowed_for_future_copy,
                "requires_verification": item.requires_verification,
                "risk_flag": item.risk_flag,
            }
            for item in row.evidence
        ]


@router.get("/duplicate-clusters")
def duplicate_clusters() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(DuplicateCluster)).all()
        return [
            {
                "id": row.id,
                "cluster_status": row.cluster_status.value,
                "cluster_score": row.cluster_score,
                "risk_flags": row.risk_flags_json,
            }
            for row in rows
        ]


@router.get("/normalization-runs")
def normalization_runs() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(NormalizationRun).order_by(NormalizationRun.id.desc())).all()
        return [
            {
                "run_id": row.run_id,
                "operation": row.operation.value,
                "status": row.status.value,
                "dry_run": row.dry_run,
            }
            for row in rows
        ]


@router.get("/manual-review-items")
def manual_review_items() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(CandidateManualReviewItem)).all()
        return [
            {
                "id": row.id,
                "review_type": row.review_type.value,
                "severity": row.severity,
                "reason": row.reason,
                "status": row.status.value,
            }
            for row in rows
        ]
