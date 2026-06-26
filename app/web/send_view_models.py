from dataclasses import dataclass


@dataclass(frozen=True)
class SendQueueView:
    id: int
    recipient: str
    status_fa: str
