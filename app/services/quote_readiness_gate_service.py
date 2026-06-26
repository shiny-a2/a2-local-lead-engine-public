from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import GateSeverity, Phase13GateName, PricingWorksheetStatus
from app.db.models.internal_pricing_worksheet import InternalPricingWorksheet
from app.db.models.quote_readiness_gate import QuoteReadinessGate
from app.db.models.scope_checklist import ScopeChecklist


class QuoteReadinessGateService:
    def __init__(self, session: Session):
        self.session = session

    def evaluate(self, opportunity_id: int) -> list[QuoteReadinessGate]:
        self.session.query(QuoteReadinessGate).filter(
            QuoteReadinessGate.opportunity_id == opportunity_id
        ).delete()
        scope = self.session.scalar(
            select(ScopeChecklist).where(ScopeChecklist.opportunity_id == opportunity_id)
        )
        worksheet = self.session.scalar(
            select(InternalPricingWorksheet).where(
                InternalPricingWorksheet.opportunity_id == opportunity_id
            )
        )
        specs = [
            (
                Phase13GateName.SCOPE_MINIMUM_GATE,
                bool(scope and scope.quote_ready),
                "Scope minimum is complete." if scope and scope.quote_ready else "Required scope answers are missing.",
            ),
            (
                Phase13GateName.MODULE_SELECTION_GATE,
                bool(worksheet and worksheet.selected_modules_json),
                "Internal modules selected." if worksheet and worksheet.selected_modules_json else "Module selection missing.",
            ),
            (
                Phase13GateName.CONTENT_READINESS_GATE,
                bool(scope and scope.completeness_score >= 70),
                "Content readiness is acceptable." if scope and scope.completeness_score >= 70 else "Content readiness needs more scope.",
            ),
            (
                Phase13GateName.TECHNICAL_REQUIREMENT_GATE,
                bool(scope and scope.completeness_score >= 70),
                "Technical requirements sufficiently known." if scope and scope.completeness_score >= 70 else "Technical requirements incomplete.",
            ),
            (
                Phase13GateName.MANUAL_PRICE_INPUT_GATE,
                bool(worksheet and worksheet.manual_base_price is not None),
                "Manual price entered." if worksheet and worksheet.manual_base_price is not None else "Manual price input required.",
            ),
            (
                Phase13GateName.HUMAN_QUOTE_APPROVAL_GATE,
                bool(
                    worksheet
                    and getattr(worksheet.pricing_status, "value", worksheet.pricing_status)
                    == PricingWorksheetStatus.APPROVED_MANUALLY.value
                ),
                "Human quote approval recorded."
                if worksheet
                and getattr(worksheet.pricing_status, "value", worksheet.pricing_status)
                == PricingWorksheetStatus.APPROVED_MANUALLY.value
                else "Human quote approval required.",
            ),
        ]
        gates = []
        for name, passed, reason in specs:
            gate = QuoteReadinessGate(
                opportunity_id=opportunity_id,
                gate_name=name,
                passed=passed,
                severity=GateSeverity.INFO if passed else GateSeverity.BLOCKER,
                reason=reason,
            )
            self.session.add(gate)
            gates.append(gate)
        self.session.flush()
        return gates
