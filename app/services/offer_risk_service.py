class OfferRiskService:
    blocked_terms = [
        "guaranteed",
        "save thousands",
        "stop paying commissions",
        "replace all",
        "losing customers",
        "competitors are ahead",
        "current system is bad",
    ]

    def blocked_reason(self, text: str) -> str | None:
        lowered = text.lower()
        for term in self.blocked_terms:
            if term in lowered:
                return f"unsupported_or_aggressive_claim:{term}"
        return None
