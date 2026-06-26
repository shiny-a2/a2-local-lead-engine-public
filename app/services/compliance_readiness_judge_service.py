class ComplianceReadinessJudgeService:
    def score(self, has_unsubscribe: bool, has_sender: bool) -> int:
        return 95 if has_unsubscribe and has_sender else 40
