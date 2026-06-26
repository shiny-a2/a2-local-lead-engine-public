from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    Phase4ReviewType,
    SearchQueryStatus,
    UrlProbeStatus,
    VerificationRunOperation,
    VerificationRunStatus,
)
from app.core.run_context import new_run_id
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_source_link import CandidateSourceLink
from app.db.models.claim_permission import ClaimPermission
from app.db.models.contact_candidate import ContactCandidate
from app.db.models.phase4_candidate_decision import Phase4CandidateDecision
from app.db.models.raw_source_record import RawSourceRecord
from app.db.models.search_query import SearchQuery
from app.db.models.verification_run import VerificationRun
from app.db.models.verified_personalization_evidence import VerifiedPersonalizationEvidence
from app.services.claim_permission_service import ClaimPermissionService
from app.services.contact_extraction_service import ContactExtractionService
from app.services.contact_verification_service import ContactVerificationService
from app.services.phase4_manual_review_service import Phase4ManualReviewService
from app.services.search_query_planner import SearchQueryPlanner
from app.services.url_probe_service import UrlProbeService
from app.services.verified_evidence_service import VerifiedEvidenceService
from app.services.web_presence_decision_service import WebPresenceDecisionService
from app.services.website_verification_service import WebsiteVerificationService
from app.settings import Settings


class Phase4VerificationOrchestrator:
    def __init__(self, settings: Settings, session: Session):
        self.settings = settings
        self.session = session

    def eligible_candidates(self, limit: int) -> list[CandidateBusiness]:
        query = select(CandidateBusiness).order_by(CandidateBusiness.id).limit(limit)
        if self.settings.phase4_require_candidate_ready:
            query = query.where(CandidateBusiness.status == "READY_FOR_WEBSITE_VERIFICATION")
        return list(self.session.scalars(query).all())

    def start_run(self, operation: VerificationRunOperation, dry_run: bool, candidates: list[CandidateBusiness]) -> VerificationRun:
        run = VerificationRun(
            run_id=new_run_id(),
            operation=operation,
            status=VerificationRunStatus.STARTED,
            dry_run=dry_run,
            input_candidate_count=len(candidates),
            metadata_json={"query_count": len(candidates) * min(3, self.settings.tavily_max_queries_per_candidate)},
        )
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def plan(self, limit: int) -> tuple[list[CandidateBusiness], int]:
        candidates = self.eligible_candidates(limit)
        planner = SearchQueryPlanner(self.settings)
        return candidates, sum(len(planner.plan_for_candidate(candidate)) for candidate in candidates)

    def full_review(self, limit: int, commit: bool) -> VerificationRun:
        candidates, _ = self.plan(limit)
        run = self.start_run(VerificationRunOperation.PHASE4_FULL_REVIEW, not commit, candidates)
        planner = SearchQueryPlanner(self.settings)
        if not commit:
            for candidate in candidates:
                for planned in planner.plan_for_candidate(candidate):
                    self.session.add(
                        SearchQuery(
                            verification_run_id=run.id,
                            candidate_business_id=candidate.id,
                            source_name="tavily",
                            query_text_redacted=planned.query_text,
                            query_type=planned.query_type,
                            cache_key=planned.cache_key,
                            dry_run=True,
                            status=SearchQueryStatus.SKIPPED_DRY_RUN,
                        )
                    )
            run.status = VerificationRunStatus.DRY_RUN_ONLY
            run.finished_at = datetime.now(UTC)
            self.session.commit()
            return run
        live_probe = self.settings.phase4_live_url_probe
        review_service = Phase4ManualReviewService(self.session)
        for candidate in candidates:
            fixture_results = (
                self._live_results(candidate) if live_probe else self._fixture_results(candidate)
            )
            web = WebsiteVerificationService(self.settings, self.session).verify_from_results(
                candidate, run.id, fixture_results, checked_live=live_probe
            )
            contact_results = list(fixture_results)
            if live_probe:
                # Surface the real source-provided email/phone so a no-website lead can still
                # have a safe contact (without it Phase 5 would always HOLD_NO_SAFE_CONTACT).
                _, _, emails = self._candidate_web_signals(candidate)
                for email in emails:
                    contact_results.append(
                        {"title": candidate.display_name, "url": None, "snippet": email}
                    )
            contacts = self._store_contacts(
                candidate, run.id, contact_results, web.official_website_domain
            )
            contact_summary = ContactVerificationService(self.session).summarize(candidate.id, run.id, contacts)
            for row in ClaimPermissionService().permissions_for_status(candidate, web.website_status, web.website_confidence):
                self.session.add(ClaimPermission(candidate_business_id=candidate.id, verification_run_id=run.id, **row))
            for row in VerifiedEvidenceService().from_web_status(
                candidate, web.website_status, [item["url"] for item in fixture_results]
            ):
                self.session.add(
                    VerifiedPersonalizationEvidence(
                        candidate_business_id=candidate.id,
                        verification_run_id=run.id,
                        **row,
                    )
                )
            decision = WebPresenceDecisionService().decide(web.website_status, contact_summary.contact_status)
            self.session.add(
                Phase4CandidateDecision(
                    candidate_business_id=candidate.id,
                    verification_run_id=run.id,
                    decision=decision["decision"],
                    decision_confidence=decision["confidence"],
                    website_status=web.website_status,
                    contact_status=contact_summary.contact_status,
                    ready_for_phase5=decision["ready_for_phase5"],
                    manual_review_required=decision["manual_review_required"],
                    reject_reason=decision["reject_reason"],
                    warnings_json=[],
                )
            )
            if web.requires_manual_review or contact_summary.manual_review_required:
                review_service.create(
                    candidate.id,
                    run.id,
                    Phase4ReviewType.UNCLEAR_WEBSITE_OWNERSHIP,
                    "Phase 4 evidence requires manual review before Phase 5.",
                )
                run.manual_review_count += 1
            run.verified_count += 1
        run.status = VerificationRunStatus.COMPLETED_WITH_WARNINGS if run.manual_review_count else VerificationRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        self.session.commit()
        return run

    def _candidate_web_signals(
        self, candidate: CandidateBusiness
    ) -> tuple[str | None, list[str], list[str]]:
        """Pull the real website / social links / emails the source connectors stored."""
        links = self.session.scalars(
            select(CandidateSourceLink).where(
                CandidateSourceLink.candidate_business_id == candidate.id
            )
        ).all()
        website: str | None = None
        socials: list[str] = []
        emails: list[str] = []
        for link in links:
            raw = self.session.get(RawSourceRecord, link.raw_source_record_id)
            if raw is None:
                continue
            if raw.raw_website and not website:
                website = raw.raw_website
            if raw.raw_email:
                emails.append(raw.raw_email)
            social_links = raw.raw_social_links_json or {}
            if isinstance(social_links, dict):
                for key, value in social_links.items():
                    if not isinstance(value, str) or not value:
                        continue
                    if value.startswith("http"):
                        socials.append(value)
                    elif "facebook" in key:
                        socials.append(f"https://facebook.com/{value.lstrip('/')}")
                    elif "instagram" in key:
                        socials.append(f"https://instagram.com/{value.lstrip('/')}")
        return website, socials, emails

    def _live_results(self, candidate: CandidateBusiness) -> list[dict]:
        """Build real verification evidence via a direct, keyless URL probe (no search API)."""
        website, socials, emails = self._candidate_web_signals(candidate)
        results: list[dict] = []
        if website:
            probed = UrlProbeService(self.settings).probe(website, dry_run=False)
            if probed.get("probe_status") == UrlProbeStatus.OK:
                snippet = (
                    f"{candidate.display_name} {candidate.city} "
                    f"{(candidate.canonical_category or '').replace('_', ' ')}"
                )
                if emails:
                    snippet += f" {emails[0]}"
                results.append(
                    {
                        "title": probed.get("title") or candidate.display_name,
                        "url": probed.get("final_url") or website,
                        "snippet": snippet,
                    }
                )
        for social in socials:
            results.append(
                {"title": candidate.display_name, "url": social, "snippet": candidate.display_name}
            )
        return results

    def _fixture_results(self, candidate: CandidateBusiness) -> list[dict]:
        name = candidate.display_name.lower()
        if "strong" in name:
            return [{"title": candidate.display_name, "url": f"https://{candidate.normalized_name.replace(' ', '')}.co.nz", "snippet": f"{candidate.display_name} {candidate.city} official website contact info@business.co.nz"}]
        if "social" in name:
            return [{"title": candidate.display_name, "url": "https://facebook.com/example", "snippet": candidate.display_name}]
        return [
            {"title": candidate.display_name, "url": "https://yellow.co.nz/example", "snippet": candidate.display_name},
            {"title": candidate.display_name, "url": "https://finda.co.nz/example", "snippet": candidate.city},
        ]

    def _store_contacts(self, candidate: CandidateBusiness, run_id: int, results: list[dict], official_domain: str | None) -> list[ContactCandidate]:
        rows = []
        extractor = ContactExtractionService()
        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')} {result.get('url', '')}"
            for item in extractor.extract_from_text(text, result.get("url"), official_domain):
                row = ContactCandidate(candidate_business_id=candidate.id, verification_run_id=run_id, **item)
                self.session.add(row)
                rows.append(row)
        self.session.commit()
        return rows
