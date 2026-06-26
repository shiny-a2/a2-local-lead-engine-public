from sqlalchemy.orm import Session

from app.core.enums import HumanSalesGateName
from app.db.models.human_sales_control_gate import HumanSalesControlGate
from app.db.models.opportunity_record import OpportunityRecord
from app.settings import Settings


class HumanSalesControlGateService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def apply(self, opportunity: OpportunityRecord) -> list[HumanSalesControlGate]:
        gates = [
            (HumanSalesGateName.NO_AUTO_PRICE_GATE, self.settings.phase12_block_automatic_price_quote),
            (HumanSalesGateName.NO_AUTO_MEETING_GATE, self.settings.phase12_block_automatic_meeting_scheduling),
            (HumanSalesGateName.NO_AUTO_REPLY_GATE, self.settings.phase12_block_automatic_response_send),
            (HumanSalesGateName.MANUAL_QUOTE_REQUIRED_GATE, True),
            (HumanSalesGateName.MANUAL_SEND_REQUIRED_GATE, True),
            (HumanSalesGateName.HUMAN_DECISION_REQUIRED_GATE, self.settings.phase12_require_human_action),
            (HumanSalesGateName.NO_AUTO_PROPOSAL_GATE, self.settings.phase12_block_automatic_proposal_send),
            (HumanSalesGateName.NO_AUTO_PAYMENT_LINK_GATE, self.settings.phase12_block_automatic_payment_link),
        ]
        rows = []
        for name, passed in gates:
            row = HumanSalesControlGate(
                opportunity_id=opportunity.id,
                gate_name=name,
                passed=passed,
                severity="INFO" if passed else "BLOCKER",
                reason="Human-only control enforced; no automatic outbound action allowed.",
            )
            self.session.add(row)
            rows.append(row)
        self.session.flush()
        return rows

    def blocks_automatic_action(self) -> bool:
        return all(
            [
                self.settings.phase12_block_automatic_response_send,
                self.settings.phase12_block_automatic_meeting_scheduling,
                self.settings.phase12_block_automatic_price_quote,
                self.settings.phase12_block_automatic_proposal_send,
                self.settings.phase12_block_automatic_payment_link,
            ]
        )
