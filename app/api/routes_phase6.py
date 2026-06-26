from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.candidate_business_insight import CandidateBusinessInsight
from app.db.models.candidate_economic_value_angle import CandidateEconomicValueAngle
from app.db.models.candidate_offer_match import CandidateOfferMatch
from app.db.models.future_email_offer_block import FutureEmailOfferBlock
from app.db.models.insight_run import InsightRun
from app.db.models.offer_playbook import OfferPlaybook
from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


def _session():
    return make_session_factory(get_settings())()


@router.get("/insight-runs")
def insight_runs() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(InsightRun).order_by(InsightRun.id.desc())).all()
        return [{"run_id": row.run_id, "status": row.status.value, "dry_run": row.dry_run} for row in rows]


@router.get("/insight-runs/{run_id}")
def insight_run(run_id: str) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(InsightRun).where(InsightRun.run_id == run_id))
        if row is None:
            return {"found": False}
        return {"found": True, "run_id": row.run_id, "input_candidate_count": row.input_candidate_count, "offer_matched_count": row.offer_matched_count}


@router.get("/candidate-businesses/{candidate_id}/insights")
def candidate_insights(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(CandidateBusinessInsight).where(CandidateBusinessInsight.candidate_business_id == candidate_id)).all()
        return [{"category": row.category, "campaign_lane": row.campaign_lane, "opportunity_summary": row.opportunity_summary} for row in rows]


@router.get("/candidate-businesses/{candidate_id}/offer-match")
def candidate_offer_match(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(CandidateOfferMatch).where(CandidateOfferMatch.candidate_business_id == candidate_id)).all()
        return [{"offer_package": row.offer_package.value, "offer_fit_score": row.offer_fit_score, "email_safe_offer_summary": row.email_safe_offer_summary} for row in rows]


@router.get("/candidate-businesses/{candidate_id}/economic-angles")
def economic_angles(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(CandidateEconomicValueAngle).where(CandidateEconomicValueAngle.candidate_business_id == candidate_id)).all()
        return [{"angle_type": row.angle_type.value, "allowed_for_future_copy": row.allowed_for_future_copy, "angle_text": row.angle_text} for row in rows]


@router.get("/candidate-businesses/{candidate_id}/future-email-blocks")
def future_email_blocks(candidate_id: int) -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(FutureEmailOfferBlock).where(FutureEmailOfferBlock.candidate_business_id == candidate_id)).all()
        return [{"block_type": row.block_type.value, "allowed_for_phase7": row.allowed_for_phase7, "block_text": row.block_text} for row in rows]


@router.get("/candidate-businesses/{candidate_id}/phase6-decision")
def phase6_decision(candidate_id: int) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(Phase6CandidateDecision).where(Phase6CandidateDecision.candidate_business_id == candidate_id).order_by(Phase6CandidateDecision.id.desc()))
        if row is None:
            return {"found": False}
        return {"found": True, "decision": row.decision.value, "ready_for_phase7": row.ready_for_phase7}


@router.get("/offer-playbooks")
def offer_playbooks() -> list[dict[str, object]]:
    with _session() as session:
        rows = session.scalars(select(OfferPlaybook)).all()
        return [{"category": row.category, "status": row.status.value, "version": row.version} for row in rows]


@router.get("/offer-playbooks/{category}")
def offer_playbook(category: str) -> dict[str, object]:
    with _session() as session:
        row = session.scalar(select(OfferPlaybook).where(OfferPlaybook.category == category))
        if row is None:
            return {"found": False}
        return {"found": True, "category": row.category, "status": row.status.value, "default_offer_package": row.default_offer_package}
