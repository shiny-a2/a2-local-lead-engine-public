from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    GateSeverity,
    Phase13GateName,
    ProposalChecklistItemStatus,
    ProposalChecklistStatus,
)
from app.db.models.proposal_checklist import ProposalChecklist
from app.db.models.proposal_checklist_item import ProposalChecklistItem
from app.db.models.proposal_readiness_gate import ProposalReadinessGate
from app.settings import Settings


class ProposalReadinessGateService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def evaluate(self, checklist: ProposalChecklist) -> list[ProposalReadinessGate]:
        self.session.query(ProposalReadinessGate).filter(
            ProposalReadinessGate.opportunity_id == checklist.opportunity_id
        ).delete()
        items = self.session.scalars(
            select(ProposalChecklistItem).where(
                ProposalChecklistItem.proposal_checklist_id == checklist.id
            )
        ).all()
        required = [item for item in items if item.required]
        ready = [item for item in required if item.status == ProposalChecklistItemStatus.READY]
        score = int((len(ready) / len(required)) * 100) if required else 100
        checklist.readiness_score = score
        checklist.status = (
            ProposalChecklistStatus.READY_FOR_HUMAN_REVIEW
            if score >= self.settings.phase13_proposal_readiness_threshold
            and len(ready) == len(required)
            else ProposalChecklistStatus.PARTIAL
        )
        gate_specs = [
            (Phase13GateName.CLIENT_NEED_SUMMARY_GATE, "client_need_summary"),
            (Phase13GateName.RECOMMENDED_PACKAGE_GATE, "recommended_package"),
            (Phase13GateName.INCLUDED_MODULES_GATE, "included_modules"),
            (Phase13GateName.EXCLUDED_ITEMS_GATE, "excluded_items"),
            (Phase13GateName.CLIENT_RESPONSIBILITIES_GATE, "client_responsibilities"),
            (Phase13GateName.MANUAL_TIMELINE_GATE, "estimated_timeline_manual"),
            (Phase13GateName.MANUAL_PRICE_GATE, "manual_price_or_range"),
            (Phase13GateName.RISK_NOTES_GATE, "risks_unknowns"),
            (Phase13GateName.HUMAN_PROPOSAL_APPROVAL_GATE, "human_approval"),
        ]
        gates = []
        by_key = {item.item_key: item for item in items}
        for gate_name, item_key in gate_specs:
            passed = by_key.get(item_key) is not None and by_key[item_key].status == ProposalChecklistItemStatus.READY
            gate = ProposalReadinessGate(
                opportunity_id=checklist.opportunity_id,
                gate_name=gate_name,
                passed=passed,
                severity=GateSeverity.INFO if passed else GateSeverity.BLOCKER,
                reason="Proposal checklist item ready." if passed else f"Missing proposal item: {item_key}",
            )
            self.session.add(gate)
            gates.append(gate)
        self.session.flush()
        return gates
