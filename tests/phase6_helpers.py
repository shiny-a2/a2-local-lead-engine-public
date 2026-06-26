from uuid import uuid4

from app.core.enums import (
    CampaignFitStatus,
    CampaignLane,
    CampaignStatus,
    CandidateStatus,
    Phase5Decision,
    PriorityTier,
    ScoringRunOperation,
    ScoringRunStatus,
    VerificationReadiness,
)
from app.db.models.campaign import Campaign
from app.db.models.campaign_fit_assessment import CampaignFitAssessment
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.scoring_run import ScoringRun


def make_phase6_ready_candidate(session, *, category="barber", lane=CampaignLane.NO_WEBSITE):
    campaign = Campaign(
        name="Auckland Local Website Pilot",
        slug=f"phase6-campaign-{uuid4().hex[:8]}",
        target_city="Auckland",
        target_country="New Zealand",
        target_categories_json=["barber", "beauty_salon", "cleaning_service"],
        status=CampaignStatus.DRAFT,
    )
    session.add(campaign)
    session.flush()
    candidate = CandidateBusiness(
        campaign_id=campaign.id,
        candidate_identity_fingerprint=f"phase6:{uuid4().hex}",
        canonical_name="Example Phase Six Studio",
        display_name="Example Phase Six Studio",
        normalized_name="example phase six studio",
        canonical_category=category,
        city="Auckland",
        suburb="Ponsonby",
        country="New Zealand",
        identity_confidence=90,
        category_confidence=90,
        data_quality_score=88,
        verification_readiness_status=VerificationReadiness.READY,
        status=CandidateStatus.READY_FOR_WEBSITE_VERIFICATION,
    )
    session.add(candidate)
    session.flush()
    scoring_run = ScoringRun(
        run_id=f"score-{uuid4().hex[:8]}",
        campaign_id=campaign.id,
        operation=ScoringRunOperation.LEAD_SCORING,
        status=ScoringRunStatus.COMPLETED,
        dry_run=False,
        scoring_profile="auckland_mvp_email_only_v1",
        score_version="v1.0",
    )
    session.add(scoring_run)
    session.flush()
    session.add(
        Phase5CandidateDecision(
            candidate_business_id=candidate.id,
            scoring_run_id=scoring_run.id,
            decision=Phase5Decision.READY_FOR_PHASE_6_INSIGHT,
            priority_tier=PriorityTier.P1_BEST_PILOT,
            ready_for_phase6=True,
        )
    )
    session.add(
        CampaignFitAssessment(
            candidate_business_id=candidate.id,
            scoring_run_id=scoring_run.id,
            campaign_lane=lane,
            campaign_fit_score=90,
            campaign_fit_status=CampaignFitStatus.FIT,
            decision_reason="fixture fit",
        )
    )
    session.commit()
    return campaign, candidate
