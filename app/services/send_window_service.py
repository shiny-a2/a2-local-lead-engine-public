from datetime import datetime
from zoneinfo import ZoneInfo

from app.settings import Settings


class SendWindowService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def check(self, now: datetime | None = None) -> tuple[bool, str]:
        if not self.settings.send_window_enabled:
            return True, "send_window_disabled"
        current = now or datetime.now(ZoneInfo(self.settings.target_timezone))
        allowed = {item.strip() for item in self.settings.send_allowed_days.split(",")}
        if current.strftime("%a") not in allowed:
            return self.settings.send_window_outside_policy != "block", "day_not_allowed"
        start_h, start_m = [int(x) for x in self.settings.send_window_start.split(":")]
        end_h, end_m = [int(x) for x in self.settings.send_window_end.split(":")]
        minutes = current.hour * 60 + current.minute
        if not (start_h * 60 + start_m <= minutes <= end_h * 60 + end_m):
            return self.settings.send_window_outside_policy != "block", "outside_send_window"
        return True, "inside_send_window"
