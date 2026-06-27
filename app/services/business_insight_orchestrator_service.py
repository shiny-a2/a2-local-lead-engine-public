from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    CampaignLane,
    FeasibilityLevel,
    InsightRunOperation,
    InsightRunStatus,
    Phase5Decision,
    Phase6Decision,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.campaign_fit_assessment import CampaignFitAssessment
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.insight_run import InsightRun
from app.db.models.offer_readiness_gate import OfferReadinessGate
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.services.business_insight_service import BusinessInsightService
from app.services.category_playbook_service import CategoryPlaybookService
from app.services.economic_value_angle_service import EconomicValueAngleService
from app.services.future_email_block_service import FutureEmailBlockService
from app.services.implementation_feasibility_service import ImplementationFeasibilityService
from app.services.module_selection_service import ModuleSelectionService
from app.services.offer_matching_service import OfferMatchingService
from app.services.offer_readiness_gate_service import OfferReadinessGateService
from app.services.pain_point_hypothesis_service import PainPointHypothesisService
from app.services.phase6_manual_review_service import Phase6ManualReviewService
from app.services.price_positioning_service import PricePositioningService
from app.settings import Settings


class BusinessInsightOrchestratorService:
    def __init__(self, session: Session, settings: Settings | None = None):
        self.session = session
        self.settings = settings or Settings()

    def eligible(self, campaign_slug: str, limit: int | None = None) -> list[tuple[CandidateBusiness, Phase5CandidateDecision, CampaignLane]]:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            return []
        decisions = self.session.scalars(
            select(Phase5CandidateDecision).where(
                Phase5CandidateDecision.ready_for_phase6.is_(True),
                Phase5CandidateDecision.decision.in_(
                    [
                        Phase5Decision.READY_FOR_PHASE_6_INSIGHT,
                        Phase5Decision.READY_FOR_PHASE_6_WITH_WARNINGS,
                    ]
                ),
            )
        ).all()
        insighted_ids: set[int] = set()
        if self.settings.pipeline_skip_processed:
            insighted_ids = set(
                self.session.scalars(select(Phase6CandidateDecision.candidate_business_id)).all()
            )
        rows: list[tuple[CandidateBusiness, Phase5CandidateDecision, CampaignLane]] = []
        seen: set[int] = set()
        for decision in decisions:
            if decision.candidate_business_id in insighted_ids or decision.candidate_business_id in seen:
                continue
            seen.add(decision.candidate_business_id)
            candidate = self.session.get(CandidateBusiness, decision.candidate_business_id)
            if candidate is None or candidate.campaign_id != campaign.id:
                continue
            fit = self.session.scalar(
                select(CampaignFitAssessment)
                .where(CampaignFitAssessment.candidate_business_id == candidate.id)
                .order_by(CampaignFitAssessment.id.desc())
            )
            rows.append((candidate, decision, fit.campaign_lane if fit else CampaignLane.FUTURE_CAMPAIGN))
        return rows[:limit] if limit else rows

    def run(self, campaign_slug: str, limit: int = 25, commit: bool = False) -> InsightRun:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        CategoryPlaybookService(self.session).seed_defaults()
        candidates = self.eligible(campaign_slug, limit)
        run = InsightRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation=InsightRunOperation.PHASE6_FULL_REVIEW,
            status=InsightRunStatus.STARTED,
            dry_run=not commit,
            input_candidate_count=len(candidates),
            metadata_json={"phase": 6, "no_email_generation": True, "external_calls": "not-called"},
        )
        self.session.add(run)
        self.session.flush()
        if not commit:
            run.status = InsightRunStatus.DRY_RUN_ONLY
            run.finished_at = datetime.now(UTC)
            self.session.commit()
            return run
        for candidate, phase5, lane in candidates:
            self._process_candidate(run, candidate, phase5, lane)
        self.session.flush()
        self._finish(run)
        self.session.commit()
        return run

    def _process_candidate(
        self,
        run: InsightRun,
        candidate: CandidateBusiness,
        phase5: Phase5CandidateDecision,
        lane: CampaignLane,
    ) -> None:
        playbook_service = CategoryPlaybookService(self.session)
        playbook = playbook_service.active_for_category(candidate.canonical_category)
        if playbook is None:
            gates = OfferReadinessGateService().build(
                has_playbook=False,
                offer_fit_score=0,
                blocked_claim_count=1,
                email_block_count=0,
                selected_module_count=0,
                phase5_decision=phase5.decision,
                complex_module_count=0,
                price_ok=True,
            )
            self._store_gates_and_review(candidate.id, run.id, gates)
            self.session.add(
                Phase6CandidateDecision(
                    candidate_business_id=candidate.id,
                    insight_run_id=run.id,
                    decision=Phase6Decision.REJECT_MISSING_PLAYBOOK,
                    ready_for_phase7=False,
                    reject_reason="missing active category playbook",
                    warnings_json=[gate["reason"] for gate in gates if not gate["passed"]],
                )
            )
            return
        modules = playbook_service.modules_for(playbook.id)
        selected, excluded = ModuleSelectionService().select(modules)
        insight = BusinessInsightService().build(candidate, run.id, lane.value)
        self.session.add(insight)
        for pain in PainPointHypothesisService().build(candidate, run.id, lane):
            self.session.add(pain)
        offer = OfferMatchingService().build(candidate, run.id, playbook, lane, selected, excluded)
        self.session.add(offer)
        angles, blocked_claims = EconomicValueAngleService().build(
            candidate.id, run.id, offer.offer_package
        )
        for angle in angles:
            self.session.add(angle)
        for claim in blocked_claims:
            self.session.add(claim)
        blocks = FutureEmailBlockService().build(candidate.id, run.id, offer, angles)
        for block in blocks:
            self.session.add(block)
        price = PricePositioningService().build(candidate.id, run.id)
        self.session.add(price)
        notes = [ImplementationFeasibilityService().note(candidate.id, run.id, module) for module in selected]
        for note in notes:
            self.session.add(note)
        complex_count = sum(
            1
            for note in notes
            if note.feasibility_level == FeasibilityLevel.NOT_RECOMMENDED_FOR_FIRST_OFFER
        )
        gates = OfferReadinessGateService().build(
            has_playbook=True,
            offer_fit_score=offer.offer_fit_score,
            blocked_claim_count=0,
            email_block_count=sum(1 for block in blocks if block.allowed_for_phase7),
            selected_module_count=len(selected),
            phase5_decision=phase5.decision,
            complex_module_count=complex_count,
            price_ok=True,
        )
        self._store_gates_and_review(candidate.id, run.id, gates)
        blockers = [gate for gate in gates if not gate["passed"]]
        decision = (
            Phase6Decision.READY_FOR_PHASE_7_EMAIL_WRITER
            if not blockers and phase5.decision == Phase5Decision.READY_FOR_PHASE_6_INSIGHT
            else Phase6Decision.READY_FOR_PHASE_7_WITH_WARNINGS
            if not blockers
            else Phase6Decision.NEEDS_MANUAL_REVIEW
        )
        self.session.add(
            Phase6CandidateDecision(
                candidate_business_id=candidate.id,
                insight_run_id=run.id,
                decision=decision,
                ready_for_phase7=decision
                in {
                    Phase6Decision.READY_FOR_PHASE_7_EMAIL_WRITER,
                    Phase6Decision.READY_FOR_PHASE_7_WITH_WARNINGS,
                },
                manual_review_required=bool(blockers),
                warnings_json=[gate["reason"] for gate in gates if not gate["passed"]],
            )
        )

    def _store_gates_and_review(self, candidate_id: int, run_id: int, gates: list[dict[str, object]]) -> None:
        for gate in gates:
            self.session.add(OfferReadinessGate(candidate_business_id=candidate_id, insight_run_id=run_id, **gate))
        for item in Phase6ManualReviewService().create(candidate_id, run_id, gates):
            self.session.add(item)

    def _finish(self, run: InsightRun) -> None:
        decisions = self.session.scalars(
            select(Phase6CandidateDecision).where(Phase6CandidateDecision.insight_run_id == run.id)
        ).all()
        run.insight_created_count = len(decisions)
        run.offer_matched_count = sum(1 for row in decisions if row.ready_for_phase7)
        run.manual_review_count = sum(1 for row in decisions if row.manual_review_required)
        run.hold_count = sum(1 for row in decisions if "HOLD" in row.decision.value)
        run.rejected_count = sum(1 for row in decisions if "REJECT" in row.decision.value)
        run.status = InsightRunStatus.COMPLETED_WITH_WARNINGS if run.manual_review_count else InsightRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
