from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ChecklistItemStatus, ChecklistStatus, ScopeChecklistType
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.scope_checklist import ScopeChecklist
from app.db.models.scope_checklist_item import ScopeChecklistItem

SCOPE_ITEMS: dict[ScopeChecklistType, list[tuple[str, str, bool]]] = {
    ScopeChecklistType.BEAUTY_SALON_BOOKING_SCOPE: [
        ("services_count", "How many treatments/services should be listed?", True),
        ("booking_type_request_or_calendar", "Is booking a request form or calendar flow?", True),
        ("staff_selection_needed", "Does the first version need staff selection?", False),
        ("gallery_assets_ready", "Are gallery or before/after images ready?", True),
        ("deposit_needed", "Is deposit support needed later?", False),
        ("reminders_needed", "Are reminder-ready fields needed later?", False),
        ("content_ready", "Is starter content ready?", True),
        ("domain_hosting_status", "What is the domain/hosting status?", True),
    ],
    ScopeChecklistType.BARBER_DIRECT_BOOKING_SCOPE: [
        ("services_prices_ready", "Are services and prices ready?", True),
        ("booking_type", "What direct booking/request path is preferred?", True),
        ("staff_profiles_needed", "Are barber/stylist profiles needed?", False),
        ("gallery_assets_ready", "Are haircut/gallery images ready?", True),
        ("location_directions_info", "Are location and directions details ready?", True),
        ("content_ready", "Is starter content ready?", True),
    ],
    ScopeChecklistType.CLEANING_QUOTE_REQUEST_SCOPE: [
        ("service_areas", "Which service areas should be listed?", True),
        ("residential_or_commercial", "Residential, commercial, or both?", True),
        ("quote_form_questions", "Which questions should the quote form ask?", True),
        ("recurring_packages", "Are recurring cleaning packages needed?", False),
        ("before_after_assets", "Are before/after assets available?", False),
        ("reviews_trust_assets", "Are reviews or trust assets ready?", True),
    ],
    ScopeChecklistType.CAFE_MENU_QR_SCOPE: [
        ("menu_ready", "Is the menu ready for an editable page?", True),
        ("qr_menu_needed", "Is a QR menu page needed?", True),
        ("daily_specials_needed", "Should daily specials be supported?", False),
        ("allergen_info_needed", "Are allergen/dietary notes needed?", False),
        ("catering_enquiry_needed", "Is catering enquiry needed?", False),
        ("table_booking_needed", "Is table booking request needed?", False),
    ],
    ScopeChecklistType.GENERIC_WEBSITE_SCOPE: [
        ("business_goal", "What is the main business goal?", True),
        ("customer_action", "What should the customer do next?", True),
        ("content_ready", "Is starter content ready?", True),
        ("domain_hosting_status", "What is the domain/hosting status?", True),
    ],
}


class ScopeChecklistService:
    def __init__(self, session: Session):
        self.session = session

    def create_for_opportunity(self, opportunity: OpportunityRecord) -> ScopeChecklist:
        existing = self.session.scalar(
            select(ScopeChecklist).where(ScopeChecklist.opportunity_id == opportunity.id)
        )
        if existing:
            return existing
        checklist_type = self._checklist_type(opportunity)
        checklist = ScopeChecklist(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            checklist_type=checklist_type,
            status=ChecklistStatus.OPEN,
            completeness_score=0,
            quote_ready=False,
            proposal_ready=False,
        )
        self.session.add(checklist)
        self.session.flush()
        for key, question, required in SCOPE_ITEMS[checklist_type]:
            self.session.add(
                ScopeChecklistItem(
                    scope_checklist_id=checklist.id,
                    item_key=key,
                    question_text=question,
                    required=required,
                    status=ChecklistItemStatus.UNANSWERED,
                )
            )
        self.session.flush()
        return checklist

    def _checklist_type(self, opportunity: OpportunityRecord) -> ScopeChecklistType:
        candidate = self.session.get(CandidateBusiness, opportunity.candidate_business_id)
        category = (candidate.canonical_category if candidate else "").lower()
        if "beauty" in category or "salon" in category:
            return ScopeChecklistType.BEAUTY_SALON_BOOKING_SCOPE
        if "barber" in category or "hair" in category:
            return ScopeChecklistType.BARBER_DIRECT_BOOKING_SCOPE
        if "clean" in category:
            return ScopeChecklistType.CLEANING_QUOTE_REQUEST_SCOPE
        if "cafe" in category or "coffee" in category:
            return ScopeChecklistType.CAFE_MENU_QR_SCOPE
        return ScopeChecklistType.GENERIC_WEBSITE_SCOPE
