from app.core.enums import ManualReviewStatus, Phase8ReviewType
from app.db.models.phase8_manual_review_item import Phase8ManualReviewItem


class Phase8ManualReviewService:
    def item(self, candidate_id: int, run_id: int, draft_id: int | None, reason: str) -> Phase8ManualReviewItem:
        return Phase8ManualReviewItem(
            candidate_business_id=candidate_id,
            email_judge_run_id=run_id,
            email_draft_variant_id=draft_id,
            review_type=Phase8ReviewType.COMPLIANCE_REVIEW,
            severity="WARNING",
            reason=reason,
            recommended_action="Review before Phase 9 human queue. Do not send.",
            evidence_json={},
            status=ManualReviewStatus.OPEN,
        )
