from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewDecisionForm:
    reviewer: str
    reason: str = ""
    notes: str | None = None
