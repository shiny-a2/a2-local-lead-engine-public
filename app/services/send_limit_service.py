from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SendLimitCounterType
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.send_limit_counter import SendLimitCounter
from app.settings import Settings


class SendLimitService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def check(self, run_id: int, domain: str) -> tuple[bool, list[str]]:
        flags = []
        today = datetime.now(UTC).strftime("%Y%m%d")
        if self._count("daily_total", today) >= self.settings.send_daily_limit:
            flags.append("daily_limit")
        if self._count("per_run", str(run_id)) >= self.settings.send_per_run_limit:
            flags.append("per_run_limit")
        if self._count("per_domain_daily", f"{today}:{domain}") >= self.settings.send_per_domain_daily_limit:
            flags.append("per_domain_daily_limit")
        return not flags, flags

    def increment(self, run_id: int, domain: str) -> None:
        today = datetime.now(UTC).strftime("%Y%m%d")
        self._inc("daily_total", SendLimitCounterType.DAILY_TOTAL, today)
        self._inc("per_run", SendLimitCounterType.PER_RUN, str(run_id))
        self._inc("per_domain_daily", SendLimitCounterType.PER_DOMAIN_DAILY, f"{today}:{domain}")

    def _count(self, prefix: str, key: str) -> int:
        row = self.session.scalar(select(SendLimitCounter).where(SendLimitCounter.counter_key == f"{prefix}:{key}"))
        return row.count if row else 0

    def _inc(self, prefix: str, counter_type: SendLimitCounterType, key: str) -> None:
        now = datetime.now(UTC)
        row = self.session.scalar(select(SendLimitCounter).where(SendLimitCounter.counter_key == f"{prefix}:{key}"))
        if row is None:
            row = SendLimitCounter(counter_key=f"{prefix}:{key}", counter_type=counter_type, count=0, window_started_at=now, window_ends_at=now + timedelta(days=1))
            self.session.add(row)
        row.count += 1
        self.session.flush()


class CooldownGuardService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def check(self, recipient_email: str, candidate_id: int, campaign_id: int) -> tuple[bool, list[str]]:
        rows = self.session.scalars(select(EmailSendQueue).where(EmailSendQueue.recipient_email == recipient_email)).all()
        if any(row.queue_status.value == "SENT_TO_PROVIDER" for row in rows):
            return False, ["recipient_cooldown"]
        return True, []
