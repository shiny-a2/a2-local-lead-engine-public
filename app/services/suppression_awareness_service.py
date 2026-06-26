from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.suppression import SuppressionList


class SuppressionAwarenessService:
    def __init__(self, session: Session):
        self.session = session

    def check(self, email: str | None) -> dict[str, object]:
        if not email:
            return {"suppressed": False, "reason": None}
        domain = email.split("@")[-1].lower() if "@" in email else None
        rows = self.session.scalars(select(SuppressionList)).all()
        for row in rows:
            if row.email and row.email.lower() == email.lower():
                return {"suppressed": True, "reason": row.reason.value}
            if domain and row.domain and row.domain.lower() == domain:
                return {"suppressed": True, "reason": row.reason.value}
        return {"suppressed": False, "reason": None}
