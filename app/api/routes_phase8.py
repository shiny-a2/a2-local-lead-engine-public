from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.email_judge_finding import EmailJudgeFinding
from app.db.models.email_judge_run import EmailJudgeRun
from app.db.models.email_rewrite_brief import EmailRewriteBrief
from app.db.models.email_variant_selection import EmailVariantSelection
from app.db.models.phase8_candidate_decision import Phase8CandidateDecision
from app.db.models.phase8_manual_review_item import Phase8ManualReviewItem
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


def _session():
    return make_session_factory(get_settings())()


@router.get("/email-judge-runs")
def email_judge_runs() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(EmailJudgeRun).order_by(EmailJudgeRun.id.desc())).all()
        return [{"run_id": row.run_id, "status": row.status.value, "judge_mode": row.judge_mode.value} for row in rows]


@router.get("/email-judge-runs/{run_id}")
def email_judge_run(run_id: str) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(EmailJudgeRun).where(EmailJudgeRun.run_id == run_id))
        if row is None:
            return {"found": False}
        return {"found": True, "run_id": row.run_id, "input_draft_count": row.input_draft_count, "approved_count": row.approved_count}


@router.get("/email-drafts/{draft_id}/judge")
def draft_judge(draft_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(EmailJudgeDecision).where(EmailJudgeDecision.email_draft_variant_id == draft_id).order_by(EmailJudgeDecision.id.desc()))
        if row is None:
            return {"found": False}
        return {"found": True, "decision": row.decision.value, "ready_for_phase9": row.ready_for_phase9}


@router.get("/email-drafts/{draft_id}/judge-findings")
def draft_judge_findings(draft_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(EmailJudgeFinding).where(EmailJudgeFinding.email_draft_variant_id == draft_id)).all()
        return [{"finding_type": row.finding_type.value, "severity": row.severity.value, "message": row.message} for row in rows]


@router.get("/email-drafts/{draft_id}/rewrite-brief")
def draft_rewrite_brief(draft_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(EmailRewriteBrief).where(EmailRewriteBrief.email_draft_variant_id == draft_id))
        if row is None:
            return {"found": False}
        return {"found": True, "rewrite_reason": row.rewrite_reason, "must_remove": row.must_remove_json}


@router.get("/email-drafts/{draft_id}/variant-selection")
def draft_variant_selection(draft_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(EmailVariantSelection).where(EmailVariantSelection.preferred_email_draft_variant_id == draft_id))
        if row is None:
            return {"found": False}
        return {"found": True, "selection_reason": row.selection_reason}


@router.get("/phase8-decisions")
def phase8_decisions() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(Phase8CandidateDecision)).all()
        return [{"candidate_business_id": row.candidate_business_id, "decision": row.decision.value, "ready_for_phase9": row.ready_for_phase9} for row in rows]


@router.get("/phase8-manual-review-items")
def phase8_manual_review_items() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(Phase8ManualReviewItem)).all()
        return [{"candidate_business_id": row.candidate_business_id, "review_type": row.review_type.value, "severity": row.severity} for row in rows]
