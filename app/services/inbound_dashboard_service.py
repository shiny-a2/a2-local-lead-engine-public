from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.bounce_event import BounceEvent
from app.db.models.human_response_task import HumanResponseTask
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.reply_classification import ReplyClassification


class InboundDashboardService:
    LABELS = {
        "POSITIVE_INTEREST": "پاسخ مثبت",
        "ASKING_PRICE": "درخواست قیمت",
        "ASKING_DETAILS": "درخواست جزئیات",
        "REQUESTED_CALL": "درخواست تماس",
        "NOT_INTERESTED": "عدم علاقه",
        "UNSUBSCRIBE_REQUEST": "لغو اشتراک",
        "OUT_OF_OFFICE": "خارج از دفتر",
        "UNKNOWN_NEEDS_REVIEW": "نیازمند بررسی",
        "hard_bounce": "برگشت سخت",
        "soft_bounce": "برگشت نرم",
        "OPEN": "وظیفه باز",
        "DONE": "بسته‌شده",
    }

    def __init__(self, session: Session):
        self.session = session

    def dashboard(self) -> dict:
        return {
            "messages": self.session.scalar(select(func.count(InboundEmailMessage.id))) or 0,
            "bounces": self.session.scalar(select(func.count(BounceEvent.id))) or 0,
            "tasks": self.session.scalar(select(func.count(HumanResponseTask.id))) or 0,
            "labels": self.LABELS,
            "no_outbound": True,
        }

    def messages(self) -> list[InboundEmailMessage]:
        return list(
            self.session.scalars(
                select(InboundEmailMessage).order_by(InboundEmailMessage.created_at.desc())
            ).all()
        )

    def classifications(self) -> list[ReplyClassification]:
        return list(self.session.scalars(select(ReplyClassification)).all())
