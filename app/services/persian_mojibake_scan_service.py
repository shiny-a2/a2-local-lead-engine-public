from pathlib import Path

MOJIBAKE_MARKERS = ("Ø", "Ù", "Û", "â€", "Ú")


class PersianMojibakeScanService:
    def scan(self, paths: list[Path] | None = None) -> dict[str, list[str]]:
        roots = paths or [Path("app/templates"), Path("app/web")]
        findings: dict[str, list[str]] = {}
        for root in roots:
            if not root.exists():
                continue
            files = [root] if root.is_file() else list(root.rglob("*"))
            for path in files:
                if path.suffix not in {".html", ".py", ".css", ".js"}:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                markers = [marker for marker in MOJIBAKE_MARKERS if marker in text]
                if markers:
                    findings[str(path)] = markers
        return findings
