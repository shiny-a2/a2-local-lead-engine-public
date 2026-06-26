import csv
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.email_draft_claim_usage import EmailDraftClaimUsage
from app.db.models.email_draft_precheck_result import EmailDraftPrecheckResult
from app.db.models.email_draft_similarity_result import EmailDraftSimilarityResult
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_generation_run import EmailGenerationRun
from app.db.models.email_subject_candidate import EmailSubjectCandidate


class Phase7ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: EmailGenerationRun) -> dict[str, object]:
        drafts = self.session.scalars(select(EmailDraftVariant).where(EmailDraftVariant.email_generation_run_id == run.id)).all()
        subjects = self.session.scalars(select(EmailSubjectCandidate).where(EmailSubjectCandidate.email_generation_run_id == run.id)).all()
        prechecks = self.session.scalars(select(EmailDraftPrecheckResult)).all()
        similarities = self.session.scalars(select(EmailDraftSimilarityResult)).all()
        claims = self.session.scalars(select(EmailDraftClaimUsage)).all()
        verdict = "PHASE_7_EMAIL_DRAFT_GENERATION_READY"
        if run.status.value == "BLOCKED_BY_AI_CONFIG":
            verdict = "PHASE_7_BLOCKED_BY_AI_CONFIG"
        elif run.blocked_count or run.manual_review_count:
            verdict = "PHASE_7_READY_WITH_DRAFT_REVIEW_GAPS"
        return {
            "run_id": run.run_id,
            "model_provider": run.model_provider,
            "model_name": run.model_name,
            "model_config_status": run.model_config_json,
            "input_candidates": run.input_candidate_count,
            "drafts_created": len(drafts),
            "drafts_blocked": run.blocked_count,
            "manual_review_count": run.manual_review_count,
            "average_word_count": round(sum(row.word_count for row in drafts) / len(drafts), 2) if drafts else 0,
            "subject_count": len(subjects),
            "campaign_lane_breakdown": dict(Counter(row.campaign_lane for row in drafts)),
            "category_breakdown": dict(Counter(row.category for row in drafts)),
            "variant_breakdown": dict(Counter(row.variant_label for row in drafts)),
            "blocked_claim_incidents": sum(1 for row in claims if not row.allowed),
            "precheck_breakdown": dict(Counter(row.precheck_status.value for row in prechecks)),
            "similarity_breakdown": dict(Counter(row.decision.value for row in similarities)),
            "prompt_injection_risk_count": sum(1 for row in prechecks if not row.prompt_injection_ok),
            "openai_calls_attempted": (run.metadata_json or {}).get("openai_calls_attempted", False),
            "warnings": [
                "Phase 7 created drafts only.",
                "No email was sent.",
                "No draft was approved for sending.",
                "All drafts require Phase 8 Compliance & Quality Judge.",
            ],
            "final_verdict": verdict,
        }

    def write(self, run: EmailGenerationRun, reports_dir: Path) -> tuple[Path, Path, Path, dict[str, object]]:
        reports_dir.mkdir(exist_ok=True)
        report = self.build(run)
        md_path = reports_dir / f"phase7-email-generation-{run.run_id}.md"
        json_path = reports_dir / f"phase7-email-generation-{run.run_id}.json"
        csv_path = reports_dir / f"phase7-drafts-review-{run.run_id}.csv"
        md_path.write_text(self._markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._write_csv(run, csv_path)
        return md_path, json_path, csv_path, report

    def _markdown(self, report: dict[str, object]) -> str:
        return "\n".join(
            [
                "# Phase 7 Email Generation Report",
                "",
                "Phase 7 creates drafts only. No email was sent or approved for sending.",
                "All drafts require Phase 8 Compliance & Quality Judge.",
                "",
                f"- run_id: {report['run_id']}",
                f"- drafts_created: {report['drafts_created']}",
                f"- drafts_blocked: {report['drafts_blocked']}",
                f"- precheck_breakdown: {report['precheck_breakdown']}",
                f"- similarity_breakdown: {report['similarity_breakdown']}",
                f"- openai_calls_attempted: {report['openai_calls_attempted']}",
                f"- final_verdict: {report['final_verdict']}",
                "",
            ]
        )

    def _write_csv(self, run: EmailGenerationRun, path: Path) -> None:
        rows = self.session.scalars(select(EmailDraftVariant).where(EmailDraftVariant.email_generation_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["draft_id", "candidate_business_id", "variant", "status", "word_count", "subject"])
            for row in rows:
                writer.writerow([row.id, row.candidate_business_id, row.variant_label, row.status.value, row.word_count, row.subject_text])
