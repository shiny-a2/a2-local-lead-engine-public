from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.enums import DomainClassification, Phase4WebsiteStatus
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_web_presence_verification import CandidateWebPresenceVerification
from app.services.domain_classifier_service import domain_from_url
from app.services.search_result_classifier import SearchResultClassifier
from app.services.website_ownership_service import WebsiteOwnershipService
from app.settings import Settings


class WebsiteVerificationService:
    def __init__(self, settings: Settings, session: Session | None = None):
        self.settings = settings
        self.session = session

    def verify_from_results(
        self,
        candidate: CandidateBusiness,
        verification_run_id: int,
        results: list[dict],
        *,
        checked_live: bool = False,
    ) -> CandidateWebPresenceVerification:
        classifier = SearchResultClassifier()
        ownership = WebsiteOwnershipService()
        classified = [classifier.classify(result, candidate) + (result,) for result in results]
        official = []
        social = []
        directory = []
        for _result_type, domain_class, result in classified:
            if domain_class == DomainClassification.SOCIAL_DOMAIN:
                social.append(result)
            elif domain_class == DomainClassification.DIRECTORY_DOMAIN:
                directory.append(result)
            else:
                confidence, _, risks = ownership.confidence(candidate, result)
                if confidence >= 50 and not risks:
                    official.append((confidence, result))
        if official:
            confidence, result = sorted(official, key=lambda item: item[0], reverse=True)[0]
            status = Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL
            url = result["url"]
            reason = "Official website evidence found."
        elif social and not directory:
            confidence = 70
            status = Phase4WebsiteStatus.SOCIAL_ONLY
            url = None
            reason = "Only social results found in checked evidence."
        elif directory and not social:
            confidence = 70
            status = Phase4WebsiteStatus.DIRECTORY_ONLY
            url = None
            reason = "Only directory results found in checked evidence."
        elif len(results) >= 2:
            confidence = 72
            status = Phase4WebsiteStatus.NO_WEBSITE_PROBABLE
            url = None
            reason = "Multiple checked sources did not show a dedicated official website."
        elif checked_live:
            # We actively probed the public listing (e.g. OpenStreetMap) and any website it
            # advertised, and resolved no working official site. Absence after a live probe is
            # conservative-but-real evidence of no dedicated website.
            confidence = 70
            status = Phase4WebsiteStatus.NO_WEBSITE_PROBABLE
            url = None
            reason = "Live public-source probe resolved no working official website."
        else:
            confidence = 20
            status = Phase4WebsiteStatus.INSUFFICIENT_EVIDENCE
            url = None
            reason = "Insufficient evidence; raw missing website alone is not enough."
        text = (
            f"I couldn't find a dedicated website for {candidate.display_name} "
            "in the public sources I checked."
        )
        row = CandidateWebPresenceVerification(
            candidate_business_id=candidate.id,
            verification_run_id=verification_run_id,
            website_status=status,
            official_website_url=url,
            official_website_domain=domain_from_url(url) if url else None,
            website_confidence=confidence,
            website_ownership_confidence=confidence,
            website_strength_score=80
            if status == Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL
            else None,
            social_only=status == Phase4WebsiteStatus.SOCIAL_ONLY,
            directory_only=status == Phase4WebsiteStatus.DIRECTORY_ONLY,
            weak_website=status == Phase4WebsiteStatus.WEAK_WEBSITE_FOUND,
            no_website_claim_allowed=status
            in {Phase4WebsiteStatus.NO_WEBSITE_PROBABLE, Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED}
            and confidence >= 70,
            no_website_claim_text=text
            if status
            in {Phase4WebsiteStatus.NO_WEBSITE_PROBABLE, Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED}
            else None,
            requires_manual_review=status
            in {Phase4WebsiteStatus.INSUFFICIENT_EVIDENCE, Phase4WebsiteStatus.NEEDS_MANUAL_REVIEW},
            decision_reason=reason,
            evidence_json={
                "result_count": len(results),
                "raw_missing_website_not_sufficient": True,
            },
            verified_at=datetime.now(UTC),
            stale_after=datetime.now(UTC)
            + timedelta(days=self.settings.phase4_verification_ttl_days),
        )
        if self.session is not None:
            self.session.add(row)
            self.session.commit()
            self.session.refresh(row)
        return row
