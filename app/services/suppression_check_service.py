from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models.suppression import SuppressionList


class SuppressionCheckService:
    def __init__(self, session: Session):
        self.session = session

    def check(self, email: str | None) -> tuple[bool, list[str]]:
        if not email:
            return True, []
        domain = email.split("@")[-1].lower() if "@" in email else ""
        row = self.session.scalar(
            select(SuppressionList).where(
                or_(SuppressionList.email == email.lower(), SuppressionList.domain == domain)
            )
        )
        if row:
            return False, [f"suppressed:{row.reason.value}"]
        return True, []
