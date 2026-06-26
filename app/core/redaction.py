from collections.abc import Mapping
from urllib.parse import parse_qsl, urlsplit, urlunsplit

SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD")
MASK = "***REDACTED***"


def is_secret_name(name: str) -> bool:
    upper = name.upper()
    return any(marker in upper for marker in SECRET_MARKERS)


def secret_presence(value: str | None) -> str:
    return "PRESENT" if value else "MISSING"


def redact_value(name: str, value: object) -> object:
    if is_secret_name(name):
        return secret_presence(str(value) if value is not None else None)
    if name.upper() == "DATABASE_URL" and value:
        return redact_database_url(str(value))
    return value


def redact_database_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.password is None:
        return url
    username = parts.username or ""
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    netloc = f"{username}:***@{host}{port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def redact_mapping(values: Mapping[str, object]) -> dict[str, object]:
    return {key: redact_value(key, value) for key, value in values.items()}


def redact_text(text: str) -> str:
    result = text
    for key, value in parse_qsl(text, keep_blank_values=True):
        if is_secret_name(key) and value:
            result = result.replace(value, MASK)
    return result

