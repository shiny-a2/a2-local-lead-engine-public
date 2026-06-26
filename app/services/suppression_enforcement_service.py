from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.send_suppression_check import SendSuppressionCheck
from app.db.models.suppression import SuppressionList


class SuppressionEnforcementService:
    def __init__(self, session: Session):
        self.session = session

    def check_queue_item(self, item: EmailSendQueue) -> tuple[bool, list[str]]:
        row = self.session.scalar(
            select(SuppressionList).where(
                or_(SuppressionList.email == item.recipient_email.lower(), SuppressionList.domain == item.recipient_domain.lower())
            )
        )
        hit = row is not None
        self.session.add(SendSuppressionCheck(email_send_queue_id=item.id, recipient_email=item.recipient_email, recipient_domain=item.recipient_domain, suppression_hit=hit, suppression_reason=row.reason.value if row else None))
        self.session.flush()
        return not hit, [row.reason.value] if row else []
