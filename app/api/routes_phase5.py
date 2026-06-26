from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.campaign_fit_assessment import CampaignFitAssessment
from app.db.models.candidate_lead_score import CandidateLeadScore
from app.db.models.outreach_readiness_gate import OutreachReadinessGate
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.pilot_batch_candidate import PilotBatchCandidate
from app.db.models.scoring_manual_review_item import ScoringManualReviewItem
from app.db.models.scoring_run import ScoringRun
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


def _session():
    return make_session_factory(get_settings())()


@router.get("/scoring-runs")
def scoring_runs() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(ScoringRun).order_by(ScoringRun.id.desc())).all()
        return [
            {
                "run_id": row.run_id,
                "status": row.status.value,
                "dry_run": row.dry_run,
                "score_version": row.score_version,
            }
            for row in rows
        ]


@router.get("/scoring-runs/{run_id}")
def scoring_run(run_id: str) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(ScoringRun).where(ScoringRun.run_id == run_id))
        if row is None:
            return {"found": False}
        return {
            "found": True,
            "run_id": row.run_id,
            "scored_count": row.scored_count,
            "ready_count": row.ready_count,
            "status": row.status.value,
        }


@router.get("/candidate-businesses/{candidate_id}/score")
def candidate_score(candidate_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(
            select(CandidateLeadScore)
            .where(CandidateLeadScore.candidate_business_id == candidate_id)
            .order_by(CandidateLeadScore.id.desc())
        )
        gates = session.scalars(
            select(OutreachReadinessGate).where(
                OutreachReadinessGate.candidate_business_id == candidate_id
            )
        ).all()
        if row is None:
            return {"found": False}
        return {
            "found": True,
            "overall_lead_score": row.overall_lead_score,
            "score_version": row.score_version,
            "scoring_profile": row.scoring_profile,
            "gates": [{"gate": gate.gate_name.value, "passed": gate.passed} for gate in gates],
        }


@router.get("/candidate-businesses/{candidate_id}/phase5-decision")
def candidate_phase5_decision(candidate_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(
            select(Phase5CandidateDecision)
            .where(Phase5CandidateDecision.candidate_business_id == candidate_id)
            .order_by(Phase5CandidateDecision.id.desc())
        )
        if row is None:
            return {"found": False}
        fit = session.scalar(
            select(CampaignFitAssessment)
            .where(CampaignFitAssessment.candidate_business_id == candidate_id)
            .order_by(CampaignFitAssessment.id.desc())
        )
        return {
            "found": True,
            "decision": row.decision.value,
            "priority_tier": row.priority_tier.value,
            "ready_for_phase6": row.ready_for_phase6,
            "campaign_lane": fit.campaign_lane.value if fit else None,
        }


@router.get("/phase5-decisions")
def phase5_decisions() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(Phase5CandidateDecision)).all()
        return [
            {
                "candidate_business_id": row.candidate_business_id,
                "decision": row.decision.value,
                "priority_tier": row.priority_tier.value,
                "ready_for_phase6": row.ready_for_phase6,
            }
            for row in rows
        ]


@router.get("/pilot-batches")
def pilot_batches() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(PilotBatchCandidate)).all()
        names = sorted({row.batch_name for row in rows})
        return [
            {
                "batch_name": name,
                "count": sum(1 for row in rows if row.batch_name == name),
            }
            for name in names
        ]


@router.get("/pilot-batches/{batch_name}")
def pilot_batch(batch_name: str) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(
            select(PilotBatchCandidate)
            .where(PilotBatchCandidate.batch_name == batch_name)
            .order_by(PilotBatchCandidate.batch_rank)
        ).all()
        return [
            {
                "candidate_business_id": row.candidate_business_id,
                "rank": row.batch_rank,
                "tier": row.priority_tier.value,
                "lane": row.campaign_lane.value,
                "selected": row.selected,
            }
            for row in rows
        ]


@router.get("/scoring-manual-review-items")
def scoring_manual_review_items() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(ScoringManualReviewItem)).all()
        return [
            {
                "candidate_business_id": row.candidate_business_id,
                "review_type": row.review_type.value,
                "severity": row.severity,
                "status": row.status.value,
            }
            for row in rows
        ]
