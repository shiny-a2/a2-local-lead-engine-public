class HumanLikenessJudgeService:
    agency_terms = ["we are a full-service agency", "synergy", "growth hacking", "world-class", "digital transformation"]
    sales_terms = ["limited time", "best price", "buy now", "act now"]

    def score(self, text: str) -> tuple[int, list[str]]:
        lowered = text.lower()
        flags = []
        if any(term in lowered for term in self.agency_terms):
            flags.append("agency_like")
        if any(term in lowered for term in self.sales_terms):
            flags.append("salesy")
        return (45, flags) if flags else (85, [])
