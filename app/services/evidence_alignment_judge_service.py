class EvidenceAlignmentJudgeService:
    def score(self, evidence_count: int) -> int:
        return 100 if evidence_count >= 2 else 50 if evidence_count == 1 else 0
