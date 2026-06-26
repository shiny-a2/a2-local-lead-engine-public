import re
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{10,}"),
    re.compile(r"(?i)(api[_-]?key|smtp_password|openai_api_key|tavily_api_key|geoapify_api_key|database_url)\s*[:=]\s*(?!PRESENT|MISSING|redacted)[^\s,]+"),
]


class SecretsAuditService:
    def scan_text(self, text: str) -> list[str]:
        findings = []
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(pattern.pattern)
        return findings

    def scan_paths(self, paths: list[Path]) -> dict[str, list[str]]:
        result = {}
        for path in paths:
            if path.name == ".env":
                result[str(path)] = ["ENV_FILE_EXCLUDED"]
                continue
            if path.is_file():
                findings = self.scan_text(path.read_text(encoding="utf-8", errors="ignore"))
                if findings:
                    result[str(path)] = findings
        return result

    def secret_status(self, settings) -> dict[str, str]:
        return settings.secret_status()
