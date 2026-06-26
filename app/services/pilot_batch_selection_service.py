from collections import Counter
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    CampaignLane,
    PriorityTier,
    ScoringRunOperation,
    ScoringRunStatus,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.campaign_fit_assessment import CampaignFitAssessment
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.pilot_batch_candidate import PilotBatchCandidate
from app.db.models.scoring_run import ScoringRun
from app.services.scoring_profile_service import SCORE_VERSION, SCORING_PROFILE


class PilotBatchSelectionService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, campaign_slug: str, batch_name: str, limit: int = 25, commit: bool = False) -> tuple[ScoringRun, list[dict[str, object]]]:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        run = ScoringRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation=ScoringRunOperation.PILOT_BATCH_SELECTION,
            status=ScoringRunStatus.STARTED,
            dry_run=not commit,
            scoring_profile=SCORING_PROFILE,
            score_version=SCORE_VERSION,
            metadata_json={"batch_name": batch_name, "no_email_generation": True},
        )
        self.session.add(run)
        self.session.flush()
        decisions = self.session.scalars(
            select(Phase5CandidateDecision).where(
                Phase5CandidateDecision.ready_for_phase6.is_(True),
                Phase5CandidateDecision.priority_tier.in_([PriorityTier.P1_BEST_PILOT, PriorityTier.P2_GOOD_WITH_CAUTION]),
            )
        ).all()
        selected: list[dict[str, object]] = []
        category_counts: Counter[str] = Counter()
        suburb_counts: Counter[str] = Counter()
        cap = max(1, int(limit * 0.4))
        ranked = sorted(decisions, key=lambda row: (0 if row.priority_tier == PriorityTier.P1_BEST_PILOT else 1, row.id))
        for decision in ranked:
            candidate = self.session.get(CandidateBusiness, decision.candidate_business_id)
            if candidate is None:
                continue
            if len(ranked) >= 5 and category_counts[candidate.canonical_category] >= cap:
                continue
            if len(ranked) >= 5 and candidate.suburb and suburb_counts[candidate.suburb] >= cap:
                continue
            lane = self._lane(decision.candidate_business_id)
            row = {
                "candidate_business_id": candidate.id,
                "batch_name": batch_name,
                "batch_rank": len(selected) + 1,
                "priority_tier": decision.priority_tier,
                "campaign_lane": lane,
                "selection_reason": "P1/P2 Phase 6 input only; not email approval.",
                "selected": True,
            }
            selected.append(row)
            category_counts[candidate.canonical_category] += 1
            if candidate.suburb:
                suburb_counts[candidate.suburb] += 1
            if len(selected) >= limit:
                break
        run.input_candidate_count = len(decisions)
        run.ready_count = len(selected)
        run.scored_count = len(selected)
        run.status = ScoringRunStatus.DRY_RUN_ONLY if not commit else ScoringRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        if commit:
            for row in selected:
                existing = self.session.scalar(
                    select(PilotBatchCandidate).where(
                        PilotBatchCandidate.batch_name == batch_name,
                        PilotBatchCandidate.candidate_business_id == row["candidate_business_id"],
                    )
                )
                if existing is None:
                    self.session.add(PilotBatchCandidate(scoring_run_id=run.id, **row))
        self.session.commit()
        return run, selected

    def _lane(self, candidate_id: int) -> CampaignLane:
        fit = self.session.scalar(
            select(CampaignFitAssessment)
            .where(CampaignFitAssessment.candidate_business_id == candidate_id)
            .order_by(CampaignFitAssessment.id.desc())
        )
        return fit.campaign_lane if fit else CampaignLane.FUTURE_CAMPAIGN
