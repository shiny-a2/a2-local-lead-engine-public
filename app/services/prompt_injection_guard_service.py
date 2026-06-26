import re


class PromptInjectionGuardService:
    suspicious_terms = ["ignore previous", "system prompt", "developer message", "send email", "forget instructions"]

    def sanitize(self, value: str) -> tuple[str, list[str]]:
        text = re.sub(r"<[^>]+>", " ", value)
        text = re.sub(r"\s+", " ", text).strip()[:1000]
        flags = [term for term in self.suspicious_terms if term in text.lower()]
        for term in flags:
            text = text.replace(term, "[removed instruction-like text]")
        return text, flags

    def sanitize_mapping(self, data: dict[str, object]) -> tuple[dict[str, object], list[str]]:
        flags: list[str] = []
        clean: dict[str, object] = {}
        for key, value in data.items():
            if isinstance(value, str):
                clean[key], item_flags = self.sanitize(value)
                flags.extend(item_flags)
            elif isinstance(value, list):
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        cleaned, item_flags = self.sanitize(item)
                        cleaned_list.append(cleaned)
                        flags.extend(item_flags)
                    else:
                        cleaned_list.append(item)
                clean[key] = cleaned_list
            else:
                clean[key] = value
        return clean, flags
