class CtaQualityJudgeService:
    urgent = ["book a call now", "buy now", "urgent", "limited offer"]

    def score(self, text: str) -> tuple[int, list[str]]:
        lowered = text.lower()
        flags = [term for term in self.urgent if term in lowered]
        if text.count("?") > 1:
            flags.append("multiple_cta")
        if flags:
            return 30, flags
        return (90, []) if text.count("?") == 1 else (40, ["missing_soft_cta"])
