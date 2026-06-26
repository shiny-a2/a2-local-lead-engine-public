from app.core.enums import EmailGenerationReviewType, ManualReviewStatus
from app.db.models.email_generation_manual_review_item import EmailGenerationManualReviewItem


class Phase7ManualReviewService:
    def item(self, candidate_id: int, run_id: int, reason: str) -> EmailGenerationManualReviewItem:
        return EmailGenerationManualReviewItem(
            candidate_business_id=candidate_id,
            email_generation_run_id=run_id,
            review_type=EmailGenerationReviewType.DRAFT_TOO_GENERIC,
            severity="WARNING",
            reason=reason,
            recommended_action="Review before Phase 8 judge; do not send.",
            evidence_json={},
            status=ManualReviewStatus.OPEN,
        )
