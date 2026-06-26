from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    OpportunityType,
    ProposalChecklistItemStatus,
    ProposalChecklistStatus,
    ProposalType,
)
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.proposal_checklist import ProposalChecklist
from app.db.models.proposal_checklist_item import ProposalChecklistItem

PROPOSAL_ITEMS = [
    ("client_need_summary", "Client need summary", True),
    ("recommended_package", "Recommended package", True),
    ("included_modules", "Included modules", True),
    ("optional_modules", "Optional modules", False),
    ("excluded_items", "Excluded items", True),
    ("client_responsibilities", "Client responsibilities", True),
    ("estimated_timeline_manual", "Manual estimated timeline", True),
    ("manual_price_or_range", "Manual price or range", True),
    ("revision_assumptions", "Revision assumptions", True),
    ("maintenance_assumptions", "Maintenance assumptions", True),
    ("risks_unknowns", "Risks and unknowns", True),
    ("human_approval", "Human approval", True),
]


class ProposalChecklistService:
    def __init__(self, session: Session):
        self.session = session

    def create_for_opportunity(self, opportunity: OpportunityRecord) -> ProposalChecklist:
        existing = self.session.scalar(
            select(ProposalChecklist).where(ProposalChecklist.opportunity_id == opportunity.id)
        )
        if existing:
            return existing
        checklist = ProposalChecklist(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            proposal_type=self._proposal_type(opportunity),
            status=ProposalChecklistStatus.OPEN,
            readiness_score=0,
        )
        self.session.add(checklist)
        self.session.flush()
        for key, label, required in PROPOSAL_ITEMS:
            self.session.add(
                ProposalChecklistItem(
                    proposal_checklist_id=checklist.id,
                    item_key=key,
                    item_label=label,
                    required=required,
                    status=ProposalChecklistItemStatus.PENDING,
                )
            )
        self.session.flush()
        return checklist

    def _proposal_type(self, opportunity: OpportunityRecord) -> ProposalType:
        return {
            OpportunityType.BOOKING_SYSTEM: ProposalType.BOOKING_SYSTEM_SITE,
            OpportunityType.QUOTE_REQUEST_SITE: ProposalType.QUOTE_REQUEST_SITE,
            OpportunityType.MENU_QR_SITE: ProposalType.MENU_QR_SITE,
            OpportunityType.WEBSITE_REFRESH: ProposalType.WEBSITE_REFRESH,
        }.get(opportunity.opportunity_type, ProposalType.STARTER_WEBSITE)
