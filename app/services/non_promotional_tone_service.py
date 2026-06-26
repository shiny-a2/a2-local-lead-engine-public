class NonPromotionalToneService:
    bad_terms = ["limited time", "best price", "buy now", "act now", "guaranteed", "amazing"]
    fear_terms = ["losing customers", "competitors are ahead"]

    def score(self, text: str) -> tuple[int, list[str]]:
        lowered = text.lower()
        flags = [term for term in self.bad_terms if term in lowered]
        flags.extend(term for term in self.fear_terms if term in lowered)
        return (40, flags) if flags else (90, [])
