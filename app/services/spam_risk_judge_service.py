class SpamRiskJudgeService:
    terms = ["free money", "urgent", "limited time", "!!!", "guaranteed", "best price", "act now"]

    def score(self, subject: str, body: str | None = None) -> tuple[int, list[str]]:
        text = f"{subject} {body or ''}".lower()
        flags = [term for term in self.terms if term in text]
        if subject.isupper() and len(subject.split()) > 1:
            flags.append("all_caps_subject")
        return (80, flags) if flags else (10, [])
