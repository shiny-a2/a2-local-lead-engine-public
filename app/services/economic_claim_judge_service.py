class EconomicClaimJudgeService:
    blocked = ["stop paying commissions", "save thousands", "guaranteed bookings", "replace all platforms"]

    def score(self, text: str) -> tuple[int, list[str]]:
        lowered = text.lower()
        flags = [term for term in self.blocked if term in lowered]
        return (0, flags) if flags else (95, [])
