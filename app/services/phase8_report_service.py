import csv
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.email_judge_disagreement import EmailJudgeDisagreement
from app.db.models.email_judge_finding import EmailJudgeFinding
from app.db.models.email_judge_run import EmailJudgeRun
from app.db.models.email_rewrite_brief import EmailRewriteBrief


class Phase8ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: EmailJudgeRun) -> dict[str, object]:
        decisions = self.session.scalars(select(EmailJudgeDecision).where(EmailJudgeDecision.email_judge_run_id == run.id)).all()
        findings = self.session.scalars(select(EmailJudgeFinding).where(EmailJudgeFinding.email_judge_run_id == run.id)).all()
        disagreements = self.session.scalars(select(EmailJudgeDisagreement).where(EmailJudgeDisagreement.email_judge_run_id == run.id)).all()
        rewrite_briefs = self.session.scalars(select(EmailRewriteBrief).where(EmailRewriteBrief.email_judge_run_id == run.id)).all()
        verdict = "PHASE_8_EMAIL_JUDGE_READY"
        if run.blocked_count:
            verdict = "PHASE_8_BLOCKED_BY_COMPLIANCE_OR_UNSAFE_CLAIMS"
        elif run.rewrite_required_count:
            verdict = "PHASE_8_READY_WITH_REWRITE_GAPS"
        elif run.judge_mode.value == "RULE_ONLY":
            verdict = "PHASE_8_RULE_JUDGE_READY_AI_JUDGE_BLOCKED_BY_CONFIG"
        return {
            "run_id": run.run_id,
            "judge_mode": run.judge_mode.value,
            "ai_judge_enabled": run.judge_mode.value == "RULE_PLUS_AI",
            "model_config_status": run.model_config_json,
            "input_draft_count": run.input_draft_count,
            "approved_for_human_review_count": run.approved_count,
            "approved_with_warnings_count": run.approved_with_warnings_count,
            "rewrite_required_count": run.rewrite_required_count,
            "manual_review_count": run.manual_review_count,
            "blocked_count": run.blocked_count,
            "top_blocker_reasons": dict(Counter(f.finding_type.value for f in findings if f.severity.value == "BLOCKER")),
            "top_warning_reasons": dict(Counter(f.finding_type.value for f in findings if f.severity.value == "WARNING")),
            "score_average": round(sum(d.quality_score for d in decisions) / len(decisions), 2) if decisions else 0,
            "variant_selection_summary": {
                "preferred": sum(1 for d in decisions if d.preferred_variant),
                "ready_for_phase9": sum(1 for d in decisions if d.ready_for_phase9),
            },
            "ai_rule_disagreement_count": len(disagreements),
            "rewrite_brief_count": len(rewrite_briefs),
            "safety_summary": {
                "email_sent": False,
                "approved_for_sending": False,
                "smtp": "not-implemented",
                "followups": "not-generated",
            },
            "warnings": [
                "Phase 8 judges drafts only.",
                "No email was sent.",
                "No draft was approved for sending.",
                "Approved means approved for human review only.",
            ],
            "final_verdict": verdict,
        }

    def write(self, run: EmailJudgeRun, reports_dir: Path) -> tuple[Path, Path, Path, Path, Path, dict[str, object]]:
        reports_dir.mkdir(exist_ok=True)
        report = self.build(run)
        md_path = reports_dir / f"phase8-judge-{run.run_id}.md"
        json_path = reports_dir / f"phase8-judge-{run.run_id}.json"
        human_csv = reports_dir / f"phase8-human-review-candidates-{run.run_id}.csv"
        rewrite_csv = reports_dir / f"phase8-rewrite-required-{run.run_id}.csv"
        blocked_csv = reports_dir / f"phase8-blocked-drafts-{run.run_id}.csv"
        md_path.write_text(self._markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._write_decision_csv(run, human_csv, "ready")
        self._write_decision_csv(run, rewrite_csv, "rewrite")
        self._write_decision_csv(run, blocked_csv, "blocked")
        return md_path, json_path, human_csv, rewrite_csv, blocked_csv, report

    def _markdown(self, report: dict[str, object]) -> str:
        return "\n".join(
            [
                "# Phase 8 Email Judge Report",
                "",
                "Phase 8 judges drafts only. No email was sent or approved for sending.",
                "",
                f"- run_id: {report['run_id']}",
                f"- judge_mode: {report['judge_mode']}",
                f"- input_draft_count: {report['input_draft_count']}",
                f"- approved_for_human_review_count: {report['approved_for_human_review_count']}",
                f"- rewrite_required_count: {report['rewrite_required_count']}",
                f"- blocked_count: {report['blocked_count']}",
                f"- final_verdict: {report['final_verdict']}",
                "",
            ]
        )

    def _write_decision_csv(self, run: EmailJudgeRun, path: Path, mode: str) -> None:
        rows = self.session.scalars(select(EmailJudgeDecision).where(EmailJudgeDecision.email_judge_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["draft_id", "candidate_business_id", "decision", "quality_score"])
            for row in rows:
                if mode == "ready" and not row.ready_for_phase9:
                    continue
                if mode == "rewrite" and not row.rewrite_required:
                    continue
                if mode == "blocked" and "BLOCKED" not in row.decision.value:
                    continue
                writer.writerow([row.email_draft_variant_id, row.candidate_business_id, row.decision.value, row.quality_score])
