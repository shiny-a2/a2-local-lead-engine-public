from dataclasses import dataclass

from app.settings import Settings


@dataclass(frozen=True)
class HumanOnlyGuardResult:
    allowed: bool
    reason: str


class HumanOnlyActionGuardService:
    blocked_actions = {
        "auto_reply",
        "auto_followup",
        "auto_quote",
        "auto_meeting",
        "auto_proposal",
        "payment_link",
        "auto_call",
    }

    def __init__(self, settings: Settings):
        self.settings = settings

    def check(self, action: str) -> HumanOnlyGuardResult:
        blocked_by_flag = {
            "auto_reply": self.settings.phase13_block_auto_reply,
            "auto_followup": self.settings.phase13_block_auto_followup,
            "auto_quote": self.settings.phase13_block_auto_quote,
            "auto_meeting": self.settings.phase13_block_auto_meeting,
            "auto_proposal": self.settings.phase13_block_auto_proposal,
            "payment_link": self.settings.phase13_block_payment_link,
            "auto_call": self.settings.phase13_block_auto_call,
        }
        if action in self.blocked_actions and blocked_by_flag.get(action, True):
            return HumanOnlyGuardResult(False, f"{action} is blocked by Phase 13 human-only guard.")
        return HumanOnlyGuardResult(True, "Internal human guidance only.")

    def assert_allowed(self, action: str) -> None:
        result = self.check(action)
        if not result.allowed:
            raise ValueError(result.reason)

    def summary(self) -> dict[str, bool]:
        return {action: not self.check(action).allowed for action in sorted(self.blocked_actions)}
