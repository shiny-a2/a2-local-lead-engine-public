from app.settings import Settings


class SubjectLineService:
    blocked = {"guaranteed", "urgent", "limited", "savings", "free money"}

    def generate(self, business_name: str, variant_label: str, settings: Settings) -> dict[str, object]:
        base = "A simple website idea"
        if variant_label == "B":
            base = f"Quick idea for {business_name}".strip()
        words = base.split()
        if len(words) > settings.email_max_subject_words:
            base = "A quick website idea"
        risks = [term for term in self.blocked if term in base.lower()]
        return {
            "subject_text": base,
            "word_count": len(base.split()),
            "risk_flags_json": risks,
            "allowed_for_judge": not risks and len(base.split()) <= settings.email_max_subject_words,
        }
