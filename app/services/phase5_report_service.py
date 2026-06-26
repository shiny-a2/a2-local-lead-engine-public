import csv
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.campaign_fit_assessment import CampaignFitAssessment
from app.db.models.candidate_lead_score import CandidateLeadScore
from app.db.models.phase5_candidate_decision import Phase5CandidateDecision
from app.db.models.pilot_batch_candidate import PilotBatchCandidate
from app.db.models.scoring_manual_review_item import ScoringManualReviewItem
from app.db.models.scoring_run import ScoringRun


class Phase5ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: ScoringRun) -> dict[str, object]:
        decisions = self.session.scalars(
            select(Phase5CandidateDecision).where(Phase5CandidateDecision.scoring_run_id == run.id)
        ).all()
        scores = self.session.scalars(
            select(CandidateLeadScore).where(CandidateLeadScore.scoring_run_id == run.id)
        ).all()
        fits = self.session.scalars(
            select(CampaignFitAssessment).where(CampaignFitAssessment.scoring_run_id == run.id)
        ).all()
        reviews = self.session.scalars(
            select(ScoringManualReviewItem).where(ScoringManualReviewItem.scoring_run_id == run.id)
        ).all()
        pilots = self.session.scalars(
            select(PilotBatchCandidate).where(PilotBatchCandidate.scoring_run_id == run.id)
        ).all()
        tier_counts = Counter(row.priority_tier.value for row in decisions)
        lane_counts = Counter(row.campaign_lane.value for row in fits)
        review_counts = Counter(row.review_type.value for row in reviews)
        verdict = "PHASE_5_LEAD_SCORING_READY"
        if run.hold_count:
            verdict = "PHASE_5_READY_BUT_CONTACT_GAPS_LIMIT_PILOT"
        if run.manual_review_count:
            verdict = "PHASE_5_READY_WITH_MANUAL_REVIEW_GAPS"
        if run.rejected_count and not run.ready_count and run.scored_count:
            verdict = "PHASE_5_BLOCKED_BY_LOW_VERIFICATION_QUALITY"
        return {
            "run_id": run.run_id,
            "scoring_profile": run.scoring_profile,
            "score_version": run.score_version,
            "input_candidate_count": run.input_candidate_count,
            "scored_candidates": len(scores),
            "ready_for_phase6_count": sum(1 for row in decisions if row.ready_for_phase6),
            "manual_review_count": run.manual_review_count,
            "hold_count": run.hold_count,
            "rejected_count": run.rejected_count,
            "priority_tier_breakdown": dict(tier_counts),
            "campaign_lane_breakdown": dict(lane_counts),
            "pilot_batch_candidates": len(pilots),
            "manual_review_reasons": dict(review_counts),
            "safety_summary": {
                "email_generation": "not-implemented",
                "email_sending": "not-implemented",
                "ai_calls": "not-called",
                "tavily_calls": "not-called",
                "external_api_calls": "not-called",
                "google_maps": "not-implemented",
                "voice": "not-implemented",
            },
            "warnings": [
                "Phase 5 does not generate emails.",
                "Phase 5 does not send outreach.",
                "Phase 5 does not authorize final sending.",
                "Phase 5 only selects candidates for Phase 6 insight/offer generation.",
            ],
            "final_verdict": verdict,
        }

    def write(self, run: ScoringRun, reports_dir: Path) -> tuple[Path, Path, Path, Path, dict[str, object]]:
        reports_dir.mkdir(exist_ok=True)
        report = self.build(run)
        md_path = reports_dir / f"phase5-scoring-{run.run_id}.md"
        json_path = reports_dir / f"phase5-scoring-{run.run_id}.json"
        pilot_path = reports_dir / f"phase5-pilot-batch-{run.run_id}.csv"
        manual_path = reports_dir / f"phase5-manual-review-{run.run_id}.csv"
        md_path.write_text(self._markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._write_pilot_csv(run, pilot_path)
        self._write_manual_csv(run, manual_path)
        return md_path, json_path, pilot_path, manual_path, report

    def _markdown(self, report: dict[str, object]) -> str:
        return "\n".join(
            [
                "# Phase 5 Scoring Report",
                "",
                "Phase 5 does not generate emails, send outreach, or authorize final sending.",
                "It only selects candidates for Phase 6 insight/offer generation.",
                "",
                f"- run_id: {report['run_id']}",
                f"- scoring_profile: {report['scoring_profile']}",
                f"- score_version: {report['score_version']}",
                f"- scored_candidates: {report['scored_candidates']}",
                f"- ready_for_phase6_count: {report['ready_for_phase6_count']}",
                f"- manual_review_count: {report['manual_review_count']}",
                f"- hold_count: {report['hold_count']}",
                f"- rejected_count: {report['rejected_count']}",
                f"- priority_tier_breakdown: {report['priority_tier_breakdown']}",
                f"- campaign_lane_breakdown: {report['campaign_lane_breakdown']}",
                f"- final_verdict: {report['final_verdict']}",
                "",
            ]
        )

    def _write_pilot_csv(self, run: ScoringRun, path: Path) -> None:
        rows = self.session.scalars(select(PilotBatchCandidate).where(PilotBatchCandidate.scoring_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["candidate_business_id", "batch_name", "rank", "tier", "lane", "selected"])
            for row in rows:
                writer.writerow([row.candidate_business_id, row.batch_name, row.batch_rank, row.priority_tier.value, row.campaign_lane.value, row.selected])

    def _write_manual_csv(self, run: ScoringRun, path: Path) -> None:
        rows = self.session.scalars(select(ScoringManualReviewItem).where(ScoringManualReviewItem.scoring_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["candidate_business_id", "review_type", "severity", "reason", "status"])
            for row in rows:
                writer.writerow([row.candidate_business_id, row.review_type.value, row.severity, row.reason, row.status.value])
