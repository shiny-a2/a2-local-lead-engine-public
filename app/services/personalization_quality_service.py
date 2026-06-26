class PersonalizationQualityService:
    def score(self, body: str, anchor_count: int | None = None) -> tuple[int, list[str]]:
        text = body.lower()
        detected = sum(token in text for token in ["auckland", "ponsonby", "barber", "studio", "website", "page", "booking"])
        anchors = anchor_count if anchor_count is not None else detected
        score = min(100, max(detected * 15, anchors * 35))
        flags: list[str] = []
        if anchors < 2:
            flags.append("too_generic")
        if "dear business owner" in text:
            flags.append("template_like")
            score = min(score, 55)
        return score, flags
