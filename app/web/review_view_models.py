from dataclasses import dataclass


@dataclass(frozen=True)
class QueueItemView:
    id: int
    candidate_business_id: int
    draft_id: int
    status: str
    campaign_lane: str | None
