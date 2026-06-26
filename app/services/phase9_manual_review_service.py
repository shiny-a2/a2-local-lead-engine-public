class Phase9ManualReviewService:
    def reason(self, code: str) -> dict[str, str]:
        return {"review_type": code, "recommended_action": "Review manually before Phase 10 queue export."}
