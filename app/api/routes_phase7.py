from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.email_draft_claim_usage import EmailDraftClaimUsage
from app.db.models.email_draft_evidence_link import EmailDraftEvidenceLink
from app.db.models.email_draft_precheck_result import EmailDraftPrecheckResult
from app.db.models.email_draft_similarity_result import EmailDraftSimilarityResult
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_generation_run import EmailGenerationRun
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


def _session():
    return make_session_factory(get_settings())()


@router.get("/email-generation-runs")
def email_generation_runs() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(EmailGenerationRun).order_by(EmailGenerationRun.id.desc())).all()
        return [{"run_id": row.run_id, "status": row.status.value, "dry_run": row.dry_run} for row in rows]


@router.get("/email-generation-runs/{run_id}")
def email_generation_run(run_id: str) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(EmailGenerationRun).where(EmailGenerationRun.run_id == run_id))
        if row is None:
            return {"found": False}
        return {"found": True, "run_id": row.run_id, "draft_created_count": row.draft_created_count, "status": row.status.value}


@router.get("/email-drafts")
def email_drafts() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(EmailDraftVariant)).all()
        return [{"id": row.id, "candidate_business_id": row.candidate_business_id, "status": row.status.value, "subject": row.subject_text} for row in rows]


@router.get("/email-drafts/{draft_id}")
def email_draft(draft_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.get(EmailDraftVariant, draft_id)
        if row is None:
            return {"found": False}
        return {"found": True, "id": row.id, "subject": row.subject_text, "body": row.body_text, "status": row.status.value}


@router.get("/email-drafts/{draft_id}/evidence")
def draft_evidence(draft_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(EmailDraftEvidenceLink).where(EmailDraftEvidenceLink.email_draft_variant_id == draft_id)).all()
        return [{"evidence_type": row.evidence_type, "source_table": row.evidence_source_table, "confidence": row.confidence} for row in rows]


@router.get("/email-drafts/{draft_id}/claims")
def draft_claims(draft_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(EmailDraftClaimUsage).where(EmailDraftClaimUsage.email_draft_variant_id == draft_id)).all()
        return [{"claim_type": row.claim_type, "allowed": row.allowed, "risk_level": row.risk_level.value} for row in rows]


@router.get("/email-drafts/{draft_id}/precheck")
def draft_precheck(draft_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(EmailDraftPrecheckResult).where(EmailDraftPrecheckResult.email_draft_variant_id == draft_id))
        if row is None:
            return {"found": False}
        return {"found": True, "status": row.precheck_status.value, "risk_flags": row.risk_flags_json}


@router.get("/email-drafts/{draft_id}/similarity")
def draft_similarity(draft_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(EmailDraftSimilarityResult).where(EmailDraftSimilarityResult.email_draft_variant_id == draft_id))
        if row is None:
            return {"found": False}
        return {"found": True, "score": row.similarity_score, "decision": row.decision.value}
