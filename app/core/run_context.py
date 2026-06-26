from dataclasses import dataclass, field
from datetime import UTC, datetime
from secrets import token_hex


def new_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{token_hex(3)}"


@dataclass(frozen=True)
class RunContext:
    actor: str = "cli"
    run_id: str = field(default_factory=new_run_id)

