from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.candidate_web_presence_verification import CandidateWebPresenceVerification
from app.db.models.claim_permission import ClaimPermission
from app.db.models.phase4_candidate_decision import Phase4CandidateDecision
from app.db.models.phase4_manual_review_item import Phase4ManualReviewItem
from app.db.models.verification_run import VerificationRun
from app.db.models.verified_personalization_evidence import VerifiedPersonalizationEvidence
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


def _session():
    return make_session_factory(get_settings())()


@router.get("/verification-runs")
def verification_runs() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(VerificationRun).order_by(VerificationRun.id.desc())).all()
        return [
            {
                "run_id": row.run_id,
                "operation": row.operation.value,
                "status": row.status.value,
                "dry_run": row.dry_run,
            }
            for row in rows
        ]


@router.get("/verification-runs/{run_id}")
def verification_run(run_id: str) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(VerificationRun).where(VerificationRun.run_id == run_id))
        if row is None:
            return {"found": False}
        return {
            "found": True,
            "run_id": row.run_id,
            "status": row.status.value,
            "input_candidate_count": row.input_candidate_count,
            "verified_count": row.verified_count,
        }


@router.get("/candidate-businesses/{candidate_id}/web-presence")
def candidate_web_presence(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(
            select(CandidateWebPresenceVerification).where(
                CandidateWebPresenceVerification.candidate_business_id == candidate_id
            )
        ).all()
        return [
            {
                "website_status": row.website_status.value,
                "official_website_url": row.official_website_url,
                "no_website_claim_allowed": row.no_website_claim_allowed,
                "requires_manual_review": row.requires_manual_review,
            }
            for row in rows
        ]


@router.get("/candidate-businesses/{candidate_id}/contacts")
def candidate_contacts(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(
            select(CandidateContactVerification).where(
                CandidateContactVerification.candidate_business_id == candidate_id
            )
        ).all()
        return [
            {
                "contact_status": row.contact_status.value,
                "outreach_contact_allowed": row.outreach_contact_allowed,
                "manual_review_required": row.manual_review_required,
            }
            for row in rows
        ]


@router.get("/candidate-businesses/{candidate_id}/verified-evidence")
def verified_evidence(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(
            select(VerifiedPersonalizationEvidence).where(
                VerifiedPersonalizationEvidence.candidate_business_id == candidate_id
            )
        ).all()
        return [
            {
                "evidence_type": row.evidence_type,
                "allowed_for_future_copy": row.allowed_for_future_copy,
                "risk_flag": row.risk_flag,
            }
            for row in rows
        ]


@router.get("/candidate-businesses/{candidate_id}/claim-permissions")
def claim_permissions(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(
            select(ClaimPermission).where(ClaimPermission.candidate_business_id == candidate_id)
        ).all()
        return [
            {
                "claim_type": row.claim_type,
                "allowed": row.allowed,
                "approved_phrasing": row.approved_phrasing,
            }
            for row in rows
        ]


@router.get("/phase4-decisions")
def phase4_decisions() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(Phase4CandidateDecision)).all()
        return [
            {
                "candidate_business_id": row.candidate_business_id,
                "decision": row.decision.value,
                "ready_for_phase5": row.ready_for_phase5,
                "manual_review_required": row.manual_review_required,
            }
            for row in rows
        ]


@router.get("/phase4-manual-review-items")
def phase4_manual_review_items() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(Phase4ManualReviewItem)).all()
        return [
            {
                "candidate_business_id": row.candidate_business_id,
                "review_type": row.review_type.value,
                "severity": row.severity,
                "reason": row.reason,
                "status": row.status.value,
            }
            for row in rows
        ]
