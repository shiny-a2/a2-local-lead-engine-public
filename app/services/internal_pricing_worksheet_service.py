from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import PricingWorksheetStatus
from app.db.models.internal_pricing_worksheet import InternalPricingWorksheet
from app.db.models.opportunity_record import OpportunityRecord


class InternalPricingWorksheetService:
    def __init__(self, session: Session):
        self.session = session

    def create_for_opportunity(self, opportunity: OpportunityRecord) -> InternalPricingWorksheet:
        existing = self.session.scalar(
            select(InternalPricingWorksheet).where(
                InternalPricingWorksheet.opportunity_id == opportunity.id
            )
        )
        if existing:
            return existing
        worksheet = InternalPricingWorksheet(
            opportunity_id=opportunity.id,
            candidate_business_id=opportunity.candidate_business_id,
            pricing_status=PricingWorksheetStatus.NEEDS_SCOPE,
            base_package=opportunity.opportunity_type.value.lower(),
            selected_modules_json={"internal_only": True},
        )
        self.session.add(worksheet)
        self.session.flush()
        return worksheet

    def update_manual_price(
        self,
        opportunity_id: int,
        manual_base_price: float,
        notes: str = "",
    ) -> InternalPricingWorksheet:
        worksheet = self.session.scalar(
            select(InternalPricingWorksheet).where(
                InternalPricingWorksheet.opportunity_id == opportunity_id
            )
        )
        if worksheet is None:
            raise ValueError("pricing worksheet not found")
        worksheet.manual_base_price = manual_base_price
        worksheet.manual_notes = notes
        worksheet.pricing_status = PricingWorksheetStatus.IN_PROGRESS
        return worksheet

    def approve_manually(
        self,
        opportunity_id: int,
        approved_by: str,
        notes: str = "",
    ) -> InternalPricingWorksheet:
        worksheet = self.session.scalar(
            select(InternalPricingWorksheet).where(
                InternalPricingWorksheet.opportunity_id == opportunity_id
            )
        )
        if worksheet is None or worksheet.manual_base_price is None:
            raise ValueError("manual price input required before quote approval")
        worksheet.final_manual_quote = worksheet.manual_base_price
        worksheet.quote_approved_by = approved_by
        worksheet.quote_approved_at = datetime.now(UTC)
        worksheet.manual_notes = notes or worksheet.manual_notes
        worksheet.pricing_status = PricingWorksheetStatus.APPROVED_MANUALLY
        return worksheet
