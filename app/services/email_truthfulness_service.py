class EmailTruthfulnessService:
    blocked_terms = {
        "you don't have a website": "absolute_no_website_claim",
        "you do not have a website": "absolute_no_website_claim",
        "guaranteed": "guaranteed_result_claim",
        "guarantee more bookings": "guaranteed_result_claim",
        "save thousands": "unsupported_economic_claim",
    }

    def score(self, text_or_blockers: str | int) -> tuple[int, list[str]]:
        if isinstance(text_or_blockers, int):
            return (100, []) if text_or_blockers == 0 else (0, ["unsupported_claim"])
        text = text_or_blockers.lower()
        flags = [flag for term, flag in self.blocked_terms.items() if term in text]
        return (60, flags) if flags else (100, [])
