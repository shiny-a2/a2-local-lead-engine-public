class A2FoundationError(Exception):
    """Base exception for foundation errors."""


class SafetyBlockedError(A2FoundationError):
    """Raised when a sensitive operation is blocked by a safety gate."""

