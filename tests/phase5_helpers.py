from uuid import uuid4

from app.core.enums import (
    CampaignStatus,
    CandidateStatus,
    ContactStatus,
    EmailType,
    Phase4Decision,
    Phase4WebsiteStatus,
    VerificationReadiness,
    VerificationRunOperation,
    VerificationRunStatus,
)
from app.db.models.campaign import Campaign
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.claim_permission import ClaimPermission
from app.db.models.phase4_candidate_decision import Phase4CandidateDecision
from app.db.models.verification_run import VerificationRun
from app.db.models.verified_personalization_evidence import VerifiedPersonalizationEvidence


def make_campaign(session):
    campaign = Campaign(
        name="Auckland Local Website Pilot",
        slug=f"auckland-local-website-pilot-{uuid4().hex[:8]}",
        target_city="Auckland",
        target_country="New Zealand",
        target_categories_json=["barber", "beauty_salon", "cleaning_service"],
        status=CampaignStatus.DRAFT,
    )
    session.add(campaign)
    session.commit()
    return campaign


def make_phase5_candidate(
    session,
    campaign=None,
    *,
    category="barber",
    website_status=Phase4WebsiteStatus.NO_WEBSITE_PROBABLE,
    contact_status=ContactStatus.GENERIC_BUSINESS_EMAIL_FOUND,
    email_type=EmailType.GENERIC_BUSINESS,
    contact_allowed=True,
    claim=True,
    evidence=True,
    identity_confidence=90,
    name="Example Auckland Barber Studio",
):
    campaign = campaign or make_campaign(session)
    candidate = CandidateBusiness(
        campaign_id=campaign.id,
        candidate_identity_fingerprint=f"{name}:{uuid4().hex}",
        canonical_name=name,
        display_name=name,
        normalized_name=name.lower(),
        canonical_category=category,
        city="Auckland",
        suburb="Ponsonby",
        country="New Zealand",
        identity_confidence=identity_confidence,
        category_confidence=90,
        data_quality_score=85,
        verification_readiness_status=VerificationReadiness.READY,
        status=CandidateStatus.READY_FOR_WEBSITE_VERIFICATION,
    )
    session.add(candidate)
    session.flush()
    run = VerificationRun(
        run_id=f"verify-{uuid4().hex[:8]}",
        campaign_id=campaign.id,
        operation=VerificationRunOperation.PHASE4_FULL_REVIEW,
        status=VerificationRunStatus.COMPLETED,
        dry_run=False,
    )
    session.add(run)
    session.flush()
    phase4_decision = (
        Phase4Decision.READY_FOR_PHASE_5_SCORING
        if website_status != Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL
        else Phase4Decision.REJECT_WEBSITE_ALREADY_STRONG
    )
    session.add(
        Phase4CandidateDecision(
            candidate_business_id=candidate.id,
            verification_run_id=run.id,
            decision=phase4_decision,
            decision_confidence=0.85,
            website_status=website_status,
            contact_status=contact_status,
            ready_for_phase5=phase4_decision == Phase4Decision.READY_FOR_PHASE_5_SCORING,
        )
    )
    session.add(
        CandidateContactVerification(
            candidate_business_id=candidate.id,
            verification_run_id=run.id,
            best_email=f"hello{uuid4().hex[:4]}@example.co.nz" if contact_status != ContactStatus.NO_CONTACT_FOUND else None,
            best_email_type=email_type if contact_status != ContactStatus.NO_CONTACT_FOUND else None,
            best_email_confidence=0.9,
            contact_status=contact_status,
            outreach_contact_allowed=contact_allowed,
            manual_review_required=not contact_allowed and contact_status != ContactStatus.NO_CONTACT_FOUND,
            decision_reason="fixture contact evidence only",
            evidence_json={"fixture": True},
        )
    )
    if claim:
        session.add(
            ClaimPermission(
                candidate_business_id=candidate.id,
                verification_run_id=run.id,
                claim_type="can_say_could_not_find_dedicated_website",
                allowed=True,
                confidence=0.8,
                approved_phrasing="I could not find a dedicated website in the public sources checked.",
                evidence_json={"fixture": True},
            )
        )
    if evidence:
        session.add(
            VerifiedPersonalizationEvidence(
                candidate_business_id=candidate.id,
                verification_run_id=run.id,
                evidence_type="verified_no_dedicated_website_probable",
                evidence_value="public sources checked",
                evidence_source="fixture",
                confidence=0.8,
                allowed_for_future_copy=True,
                supporting_urls_json=["https://example.co.nz"],
            )
        )
    session.commit()
    return campaign, candidate
