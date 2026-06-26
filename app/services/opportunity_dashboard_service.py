from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.phase12_human_task import Phase12HumanTask
from app.db.models.pricing_guidance_record import PricingGuidanceRecord


class OpportunityDashboardService:
    STATUS_FA = {
        "QUALIFIED_INTEREST": "علاقه‌مند",
        "ASKED_PRICE": "درخواست قیمت",
        "ASKED_DETAILS": "درخواست جزئیات",
        "CALL_REQUESTED": "درخواست تماس",
        "CLOSED_NOT_INTERESTED": "بسته‌شده: عدم علاقه",
    }

    def __init__(self, session: Session):
        self.session = session

    def dashboard(self) -> dict:
        opportunities = self.session.scalars(select(OpportunityRecord)).all()
        tasks = self.session.scalars(select(Phase12HumanTask)).all()
        pricing = self.session.scalars(select(PricingGuidanceRecord)).all()
        return {
            "opportunities": len(opportunities),
            "tasks": len(tasks),
            "pricing_guidance": len(pricing),
            "no_outbound": True,
            "labels": self.STATUS_FA,
        }

    def opportunities(self) -> list[OpportunityRecord]:
        return list(self.session.scalars(select(OpportunityRecord)).all())
