from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    CampaignFitStatus,
    ContactStatus,
    EmailType,
    GateSeverity,
    Phase4Decision,
    Phase4WebsiteStatus,
    Phase5Decision,
    PriorityTier,
    ReplyProbabilityBand,
    ScoringRunOperation,
    ScoringRunStatus,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.campaign_fit_assessment import CampaignFitAssessment
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.candidate_lead_score import CandidateLeadScore
from app.db.models.claim_permission import ClaimPermission
from app.db.models.outreach_readiness_gate import OutreachReadinessGate
from app.db.models.phase4_candidate_decision import Phase4CandidateDecision
from app.db.models.phase4_manual_review_item import Phase4ManualReviewItem
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.scoring_run import ScoringRun
from app.services.campaign_selection_service import CampaignSelectionService
from app.services.compliance_scoring_service import ComplianceScoringService
from app.services.personalization_readiness_service import PersonalizationReadinessService
from app.services.readiness_gate_service import ReadinessGateService
from app.services.risk_penalty_service import RiskPenaltyService
from app.services.scoring_manual_review_service import ScoringManualReviewService
from app.services.scoring_profile_service import (
    SCORE_VERSION,
    SCORING_PROFILE,
    ScoringProfileService,
)
from app.services.suppression_awareness_service import SuppressionAwarenessService


class LeadScoringService:
    website_scores = {
        Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED: 100.0,
        Phase4WebsiteStatus.NO_WEBSITE_PROBABLE: 85.0,
        Phase4WebsiteStatus.SOCIAL_ONLY: 80.0,
        Phase4WebsiteStatus.DIRECTORY_ONLY: 75.0,
        Phase4WebsiteStatus.WEAK_WEBSITE_FOUND: 55.0,
        Phase4WebsiteStatus.WEBSITE_FOUND_UNCLEAR: 35.0,
        Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL: 0.0,
    }
    fit_scores = {"barber": 90.0, "beauty_salon": 90.0, "cleaning_service": 80.0}

    def __init__(self, session: Session):
        self.session = session

    def eligible_candidates(self, campaign_slug: str, limit: int | None = None) -> list[tuple[CandidateBusiness, Phase4CandidateDecision]]:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        query = select(CandidateBusiness)
        if campaign:
            query = query.where(CandidateBusiness.campaign_id == campaign.id)
        candidates = self.session.scalars(query.order_by(CandidateBusiness.id)).all()
        rows: list[tuple[CandidateBusiness, Phase4CandidateDecision]] = []
        for candidate in candidates:
            decision = self._latest_phase4(candidate.id)
            if decision and decision.decision in {
                Phase4Decision.READY_FOR_PHASE_5_SCORING,
                Phase4Decision.READY_FOR_PHASE_5_WITH_WARNINGS,
            }:
                rows.append((candidate, decision))
        return rows[:limit] if limit else rows

    def score_candidates(self, campaign_slug: str, limit: int = 50, commit: bool = False) -> ScoringRun:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        eligible = self.eligible_candidates(campaign_slug, limit)
        run = ScoringRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation=ScoringRunOperation.LEAD_SCORING,
            status=ScoringRunStatus.STARTED,
            dry_run=not commit,
            scoring_profile=SCORING_PROFILE,
            score_version=SCORE_VERSION,
            input_candidate_count=len(eligible),
            metadata_json={"phase": 5, "no_outreach": True, "external_calls": "not-called"},
        )
        self.session.add(run)
        self.session.flush()
        self.session.add(ScoringProfileService().snapshot(run.id))
        if not commit:
            run.status = ScoringRunStatus.DRY_RUN_ONLY
            run.finished_at = datetime.now(UTC)
            self.session.commit()
            return run

        for candidate, phase4 in eligible:
            self._score_one(run, candidate, phase4)
        self.session.flush()
        self._finish_counts(run)
        self.session.commit()
        return run

    def _score_one(self, run: ScoringRun, candidate: CandidateBusiness, phase4: Phase4CandidateDecision) -> None:
        contact = self._latest_contact(candidate.id)
        claim_count = self.session.scalar(
            select(ClaimPermission)
            .where(ClaimPermission.candidate_business_id == candidate.id, ClaimPermission.allowed.is_(True))
            .limit(1)
        )
        claim_permission_count = 1 if claim_count else 0
        unresolved_reviews = len(
            self.session.scalars(
                select(Phase4ManualReviewItem).where(
                    Phase4ManualReviewItem.candidate_business_id == candidate.id,
                    Phase4ManualReviewItem.status == "OPEN",
                )
            ).all()
        )
        campaign_fit = CampaignSelectionService().assess(phase4.website_status, candidate.canonical_category)
        personalization = PersonalizationReadinessService(self.session).evaluate(candidate.id)
        compliance = ComplianceScoringService().score(contact, unresolved_reviews)
        suppression = SuppressionAwarenessService(self.session).check(contact.best_email if contact else None)
        gates = ReadinessGateService().build(
            phase4_decision=phase4.decision,
            website_status=phase4.website_status,
            contact_status=phase4.contact_status,
            contact_allowed=bool(contact and contact.outreach_contact_allowed),
            claim_permission_count=claim_permission_count,
            personalization_passed=bool(personalization["passed"]),
            compliance_blocker=bool(compliance["blocker"]),
            unresolved_reviews=unresolved_reviews,
            campaign_lane=campaign_fit.lane,
            identity_confidence=candidate.identity_confidence,
            suppressed=bool(suppression["suppressed"]),
        )
        contact_score = self._contact_score(contact)
        website_score = self.website_scores.get(phase4.website_status, 0.0)
        fit_score = self.fit_scores.get(candidate.canonical_category, 20.0)
        compliance_warnings = cast(list[str], compliance["warnings"])
        warnings = [str(item) for item in compliance_warnings]
        if suppression["suppressed"]:
            warnings.append("suppression_hit")
        risk_penalty, risk_flags = RiskPenaltyService().calculate(candidate, warnings)
        overall = (
            website_score * 0.30
            + fit_score * 0.20
            + contact_score * 0.20
            + cast(float, personalization["score"]) * 0.20
            + cast(float, compliance["score"]) * 0.10
            - risk_penalty
        )
        score = CandidateLeadScore(
            candidate_business_id=candidate.id,
            scoring_run_id=run.id,
            overall_lead_score=max(0.0, round(overall, 2)),
            website_opportunity_score=website_score,
            business_fit_score=fit_score,
            contact_readiness_score=contact_score,
            personalization_potential_score=cast(float, personalization["score"]),
            compliance_safety_score=cast(float, compliance["score"]),
            reply_probability_band=self._band(overall),
            risk_penalty=risk_penalty,
            score_version=SCORE_VERSION,
            scoring_profile=SCORING_PROFILE,
            positive_reasons_json=self._positive_reasons(phase4.website_status, contact, personalization),
            negative_reasons_json=warnings,
            score_reasons_json={
                "website_opportunity_score": website_score,
                "business_fit_score": fit_score,
                "contact_readiness_score": contact_score,
                "personalization_potential_score": personalization["score"],
                "compliance_safety_score": compliance["score"],
                "risk_penalty": risk_penalty,
            },
            risk_flags_json=risk_flags,
        )
        self.session.add(score)
        self.session.add(
            CampaignFitAssessment(
                candidate_business_id=candidate.id,
                scoring_run_id=run.id,
                campaign_lane=campaign_fit.lane,
                campaign_fit_score=campaign_fit.score,
                campaign_fit_status=campaign_fit.status,
                decision_reason=campaign_fit.reason,
            )
        )
        for gate in gates:
            self.session.add(OutreachReadinessGate(candidate_business_id=candidate.id, scoring_run_id=run.id, **gate))
        for item in ScoringManualReviewService().create_for_failures(candidate.id, run.id, gates):
            self.session.add(item)
        self.session.add(self._decision(candidate, phase4, campaign_fit.status, campaign_fit.lane, contact, score, gates, suppression))

    def _decision(self, candidate, phase4, fit_status, lane, contact, score, gates, suppression) -> Phase5CandidateDecision:
        blockers = [gate for gate in gates if not gate["passed"] and gate["severity"] == GateSeverity.BLOCKER]
        warnings = [gate["reason"] for gate in gates if not gate["passed"]]
        if suppression["suppressed"]:
            decision, tier = Phase5Decision.HOLD_SUPPRESSED_CONTACT, PriorityTier.P3_HOLD_LATER
        elif phase4.website_status == Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL:
            decision, tier = Phase5Decision.REJECT_WEBSITE_ALREADY_STRONG, PriorityTier.P5_REJECTED
        elif fit_status == CampaignFitStatus.NOT_FIT:
            decision, tier = Phase5Decision.REJECT_OUT_OF_SCOPE, PriorityTier.P5_REJECTED
        elif phase4.website_status == Phase4WebsiteStatus.WEAK_WEBSITE_FOUND:
            decision, tier = Phase5Decision.HOLD_FOR_FUTURE_WEAK_WEBSITE_CAMPAIGN, PriorityTier.P3_HOLD_LATER
        elif contact is None or contact.contact_status == ContactStatus.NO_CONTACT_FOUND:
            decision, tier = Phase5Decision.HOLD_NO_SAFE_CONTACT, PriorityTier.P3_HOLD_LATER
        elif any(gate["gate_name"].value == "personalization_evidence_gate" for gate in blockers):
            decision, tier = Phase5Decision.REJECT_INSUFFICIENT_PERSONALIZATION_EVIDENCE, PriorityTier.P5_REJECTED
        elif blockers:
            decision, tier = Phase5Decision.NEEDS_MANUAL_REVIEW, PriorityTier.P4_MANUAL_REVIEW
        elif score.overall_lead_score >= 80:
            decision, tier = Phase5Decision.READY_FOR_PHASE_6_INSIGHT, PriorityTier.P1_BEST_PILOT
        elif score.overall_lead_score >= 65:
            decision, tier = Phase5Decision.READY_FOR_PHASE_6_WITH_WARNINGS, PriorityTier.P2_GOOD_WITH_CAUTION
        else:
            decision, tier = Phase5Decision.REJECT_LOW_FIT, PriorityTier.P5_REJECTED
        return Phase5CandidateDecision(
            candidate_business_id=candidate.id,
            scoring_run_id=score.scoring_run_id,
            decision=decision,
            priority_tier=tier,
            ready_for_phase6=decision in {Phase5Decision.READY_FOR_PHASE_6_INSIGHT, Phase5Decision.READY_FOR_PHASE_6_WITH_WARNINGS},
            manual_review_required=tier == PriorityTier.P4_MANUAL_REVIEW,
            hold_reason=decision.value if tier == PriorityTier.P3_HOLD_LATER else None,
            reject_reason=decision.value if tier == PriorityTier.P5_REJECTED else None,
            warnings_json=warnings,
        )

    def _contact_score(self, contact: CandidateContactVerification | None) -> float:
        if contact is None:
            return 0.0
        if contact.best_email_type == EmailType.GENERIC_BUSINESS and contact.outreach_contact_allowed:
            return 100.0
        if contact.best_email_type == EmailType.ROLE_BASED and contact.outreach_contact_allowed:
            return 90.0
        if contact.contact_status == ContactStatus.CONTACT_FORM_FOUND:
            return 40.0
        if contact.contact_status == ContactStatus.PHONE_ONLY:
            return 20.0
        if contact.contact_status == ContactStatus.SOCIAL_ONLY_CONTACT:
            return 15.0
        if contact.contact_status == ContactStatus.PERSONAL_EMAIL_FOUND_BLOCKED:
            return -50.0
        return 0.0

    def _band(self, overall: float) -> ReplyProbabilityBand:
        if overall >= 80:
            return ReplyProbabilityBand.HIGH
        if overall >= 60:
            return ReplyProbabilityBand.MEDIUM
        return ReplyProbabilityBand.LOW

    def _positive_reasons(self, website_status, contact, personalization) -> list[str]:
        reasons = [f"website_status:{website_status.value}"]
        if contact and contact.outreach_contact_allowed:
            reasons.append("low_risk_contact_candidate")
        if personalization["passed"]:
            reasons.append("verified_personalization_evidence_present")
        return reasons

    def _latest_phase4(self, candidate_id: int) -> Phase4CandidateDecision | None:
        return self.session.scalar(
            select(Phase4CandidateDecision)
            .where(Phase4CandidateDecision.candidate_business_id == candidate_id)
            .order_by(Phase4CandidateDecision.id.desc())
        )

    def _latest_contact(self, candidate_id: int) -> CandidateContactVerification | None:
        return self.session.scalar(
            select(CandidateContactVerification)
            .where(CandidateContactVerification.candidate_business_id == candidate_id)
            .order_by(CandidateContactVerification.id.desc())
        )

    def _finish_counts(self, run: ScoringRun) -> None:
        decisions = self.session.scalars(
            select(Phase5CandidateDecision).where(Phase5CandidateDecision.scoring_run_id == run.id)
        ).all()
        run.scored_count = len(decisions)
        run.ready_count = sum(1 for row in decisions if row.ready_for_phase6)
        run.manual_review_count = sum(1 for row in decisions if row.manual_review_required)
        run.hold_count = sum(
            1 for row in decisions if self._enum_value(row.priority_tier) == PriorityTier.P3_HOLD_LATER
        )
        run.rejected_count = sum(
            1 for row in decisions if self._enum_value(row.priority_tier) == PriorityTier.P5_REJECTED
        )
        run.status = ScoringRunStatus.COMPLETED_WITH_WARNINGS if run.manual_review_count or run.hold_count else ScoringRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)

    def _enum_value(self, value: object) -> str:
        raw = getattr(value, "value", str(value))
        return str(raw).split(".")[-1]
