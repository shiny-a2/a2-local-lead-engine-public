import csv
import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.blocked_offer_claim import BlockedOfferClaim
from app.db.models.candidate_business_insight import CandidateBusinessInsight
from app.db.models.candidate_economic_value_angle import CandidateEconomicValueAngle
from app.db.models.candidate_offer_match import CandidateOfferMatch
from app.db.models.future_email_offer_block import FutureEmailOfferBlock
from app.db.models.implementation_feasibility_note import ImplementationFeasibilityNote
from app.db.models.insight_run import InsightRun
from app.db.models.offer_manual_review_item import OfferManualReviewItem
from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.db.models.price_positioning_recommendation import PricePositioningRecommendation


class Phase6ReportService:
    def __init__(self, session: Session):
        self.session = session

    def build(self, run: InsightRun) -> dict[str, object]:
        insights = self.session.scalars(select(CandidateBusinessInsight).where(CandidateBusinessInsight.insight_run_id == run.id)).all()
        offers = self.session.scalars(select(CandidateOfferMatch).where(CandidateOfferMatch.insight_run_id == run.id)).all()
        angles = self.session.scalars(select(CandidateEconomicValueAngle).where(CandidateEconomicValueAngle.insight_run_id == run.id)).all()
        blocks = self.session.scalars(select(FutureEmailOfferBlock).where(FutureEmailOfferBlock.insight_run_id == run.id)).all()
        decisions = self.session.scalars(select(Phase6CandidateDecision).where(Phase6CandidateDecision.insight_run_id == run.id)).all()
        claims = self.session.scalars(select(BlockedOfferClaim).where(BlockedOfferClaim.insight_run_id == run.id)).all()
        notes = self.session.scalars(select(ImplementationFeasibilityNote).where(ImplementationFeasibilityNote.insight_run_id == run.id)).all()
        prices = self.session.scalars(select(PricePositioningRecommendation).where(PricePositioningRecommendation.insight_run_id == run.id)).all()
        reviews = self.session.scalars(select(OfferManualReviewItem).where(OfferManualReviewItem.insight_run_id == run.id)).all()
        verdict = "PHASE_6_INSIGHT_OFFER_ENGINE_READY"
        if run.manual_review_count:
            verdict = "PHASE_6_READY_WITH_OFFER_REVIEW_GAPS"
        if not offers and run.input_candidate_count:
            verdict = "PHASE_6_BLOCKED_BY_MISSING_CATEGORY_PLAYBOOKS"
        return {
            "run_id": run.run_id,
            "total_input_candidates": run.input_candidate_count,
            "insights_created": len(insights),
            "offer_matches": len(offers),
            "ready_for_phase7_count": sum(1 for row in decisions if row.ready_for_phase7),
            "manual_review_count": run.manual_review_count,
            "hold_count": run.hold_count,
            "rejected_count": run.rejected_count,
            "category_breakdown": dict(Counter(row.category for row in insights)),
            "campaign_lane_breakdown": dict(Counter(row.campaign_lane for row in insights)),
            "offer_package_breakdown": dict(Counter(row.offer_package.value for row in offers)),
            "economic_angle_breakdown": dict(Counter(row.angle_type.value for row in angles)),
            "blocked_claims_count": len(claims),
            "unsupported_economic_claim_count": len(claims),
            "future_email_offer_block_count": len(blocks),
            "price_positioning_summary": dict(Counter(row.price_positioning.value for row in prices)),
            "implementation_risk_summary": dict(Counter(row.risk_level.value for row in notes)),
            "decision_breakdown": dict(Counter(row.decision.value for row in decisions)),
            "manual_review_reasons": dict(Counter(row.review_type.value for row in reviews)),
            "safety_summary": {
                "email_body": "not-generated",
                "subject_lines": "not-generated",
                "ai_calls": "not-called",
                "external_api_calls": "not-called",
                "tavily_calls": "not-called",
                "email_sending": "not-implemented",
                "google_maps": "not-implemented",
                "voice": "not-implemented",
            },
            "warnings": [
                "Phase 6 does not write emails.",
                "Phase 6 does not generate subject lines.",
                "Phase 6 does not call AI.",
                "Phase 6 does not send outreach.",
                "Phase 6 only prepares structured insight/offer blocks for Phase 7.",
            ],
            "final_verdict": verdict,
        }

    def write(self, run: InsightRun, reports_dir: Path) -> tuple[Path, Path, Path, Path, dict[str, object]]:
        reports_dir.mkdir(exist_ok=True)
        report = self.build(run)
        md_path = reports_dir / f"phase6-insights-{run.run_id}.md"
        json_path = reports_dir / f"phase6-insights-{run.run_id}.json"
        blocks_path = reports_dir / f"phase6-offer-blocks-{run.run_id}.csv"
        manual_path = reports_dir / f"phase6-manual-review-{run.run_id}.csv"
        md_path.write_text(self._markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        self._write_blocks(run, blocks_path)
        self._write_manual(run, manual_path)
        return md_path, json_path, blocks_path, manual_path, report

    def _markdown(self, report: dict[str, object]) -> str:
        return "\n".join(
            [
                "# Phase 6 Insight Offer Report",
                "",
                "Phase 6 does not write emails, generate subject lines, call AI, or send outreach.",
                "",
                f"- run_id: {report['run_id']}",
                f"- insights_created: {report['insights_created']}",
                f"- offer_matches: {report['offer_matches']}",
                f"- ready_for_phase7_count: {report['ready_for_phase7_count']}",
                f"- offer_package_breakdown: {report['offer_package_breakdown']}",
                f"- blocked_claims_count: {report['blocked_claims_count']}",
                f"- future_email_offer_block_count: {report['future_email_offer_block_count']}",
                f"- final_verdict: {report['final_verdict']}",
                "",
            ]
        )

    def _write_blocks(self, run: InsightRun, path: Path) -> None:
        rows = self.session.scalars(select(FutureEmailOfferBlock).where(FutureEmailOfferBlock.insight_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["candidate_business_id", "block_type", "allowed_for_phase7", "block_text"])
            for row in rows:
                writer.writerow([row.candidate_business_id, row.block_type.value, row.allowed_for_phase7, row.block_text])

    def _write_manual(self, run: InsightRun, path: Path) -> None:
        rows = self.session.scalars(select(OfferManualReviewItem).where(OfferManualReviewItem.insight_run_id == run.id)).all()
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["candidate_business_id", "review_type", "severity", "reason", "status"])
            for row in rows:
                writer.writerow([row.candidate_business_id, row.review_type.value, row.severity, row.reason, row.status.value])
