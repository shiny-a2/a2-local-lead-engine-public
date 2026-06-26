import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.candidate_web_presence_verification import CandidateWebPresenceVerification
from app.db.models.claim_permission import ClaimPermission
from app.db.models.phase4_manual_review_item import Phase4ManualReviewItem
from app.db.models.verification_run import VerificationRun
from app.db.models.verified_personalization_evidence import VerifiedPersonalizationEvidence
from app.services.phase4_manual_review_service import Phase4ManualReviewService

PHASE4_WARNING = (
    "Phase 4 verifies evidence only. It does not authorize outreach, generate email copy, "
    "send messages, or allow absolute no-website claims. Contact found does not equal "
    "permission to send."
)


class Phase4ReportService:
    def __init__(self, session: Session):
        self.session = session

    def summary(self, run: VerificationRun) -> dict:
        websites = self.session.scalars(
            select(CandidateWebPresenceVerification).where(
                CandidateWebPresenceVerification.verification_run_id == run.id
            )
        ).all()
        contacts = self.session.scalars(
            select(CandidateContactVerification).where(
                CandidateContactVerification.verification_run_id == run.id
            )
        ).all()
        claims = self.session.scalars(
            select(ClaimPermission).where(ClaimPermission.verification_run_id == run.id)
        ).all()
        evidence = self.session.scalars(
            select(VerifiedPersonalizationEvidence).where(
                VerifiedPersonalizationEvidence.verification_run_id == run.id
            )
        ).all()
        reviews = self.session.scalars(
            select(Phase4ManualReviewItem).where(Phase4ManualReviewItem.verification_run_id == run.id)
        ).all()
        website_counts = Counter(item.website_status.value for item in websites)
        contact_counts = Counter(item.contact_status.value for item in contacts)
        verdict = "PHASE_4_WEB_PRESENCE_VERIFICATION_READY"
        if reviews:
            verdict = "PHASE_4_READY_WITH_MANUAL_REVIEW_GAPS"
        if run.status.value == "DRY_RUN_ONLY":
            verdict = "PHASE_4_DRY_RUN_READY_WITH_LIVE_CONFIG_GAPS"
        if run.status.value in {"BLOCKED_BY_SAFETY", "BLOCKED_BY_CONFIG", "BLOCKED_BY_BUDGET"}:
            verdict = "PHASE_4_BLOCKED_BY_SAFETY_OR_BUDGET"
        return {
            "warning": PHASE4_WARNING,
            "run_id": run.run_id,
            "candidates_processed": run.input_candidate_count,
            "candidates_skipped": max(0, run.input_candidate_count - run.verified_count),
            "website_status_breakdown": dict(website_counts),
            "official_websites_found": website_counts.get("WEBSITE_FOUND_OFFICIAL", 0),
            "weak_websites_found": website_counts.get("WEAK_WEBSITE_FOUND", 0),
            "social_only_count": website_counts.get("SOCIAL_ONLY", 0),
            "directory_only_count": website_counts.get("DIRECTORY_ONLY", 0),
            "no_website_probable_count": website_counts.get("NO_WEBSITE_PROBABLE", 0),
            "insufficient_evidence_count": website_counts.get("INSUFFICIENT_EVIDENCE", 0),
            "contact_status_breakdown": dict(contact_counts),
            "allowed_contact_candidate_count": sum(1 for item in contacts if item.outreach_contact_allowed),
            "manual_review_count": len(reviews),
            "claim_permission_breakdown": Counter(item.claim_type for item in claims),
            "verified_evidence_breakdown": Counter(item.evidence_type for item in evidence),
            "budget_usage_estimate": run.metadata_json.get("query_count", 0) if run.metadata_json else 0,
            "safety_summary": "No outreach/email/AI/Google/voice/contact-form automation.",
            "final_verdict": verdict,
        }

    def write(self, run: VerificationRun, reports_dir: Path) -> tuple[Path, Path, Path, dict]:
        reports_dir.mkdir(parents=True, exist_ok=True)
        summary = self.summary(run)
        md_path = reports_dir / f"phase4-verification-{run.run_id}.md"
        json_path = reports_dir / f"phase4-verification-{run.run_id}.json"
        csv_path = reports_dir / f"phase4-manual-review-{run.run_id}.csv"
        json_ready = dict(summary)
        json_ready["claim_permission_breakdown"] = dict(json_ready["claim_permission_breakdown"])
        json_ready["verified_evidence_breakdown"] = dict(json_ready["verified_evidence_breakdown"])
        json_path.write_text(json.dumps(json_ready, indent=2, sort_keys=True), encoding="utf-8")
        lines = ["# Phase 4 Verification Report", "", PHASE4_WARNING, ""]
        lines.extend(f"- {key}: `{value}`" for key, value in json_ready.items() if key != "warning")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        rows = self.session.scalars(
            select(Phase4ManualReviewItem).where(Phase4ManualReviewItem.verification_run_id == run.id)
        ).all()
        Phase4ManualReviewService(self.session).export_csv(list(rows), csv_path)
        return md_path, json_path, csv_path, json_ready
