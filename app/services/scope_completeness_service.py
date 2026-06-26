from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ChecklistItemStatus, ChecklistStatus
from app.db.models.scope_checklist import ScopeChecklist
from app.db.models.scope_checklist_item import ScopeChecklistItem
from app.settings import Settings


class ScopeCompletenessService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def calculate(self, checklist: ScopeChecklist) -> int:
        items = self.session.scalars(
            select(ScopeChecklistItem).where(ScopeChecklistItem.scope_checklist_id == checklist.id)
        ).all()
        required = [item for item in items if item.required]
        answered = [item for item in required if item.status == ChecklistItemStatus.ANSWERED]
        score = int((len(answered) / len(required)) * 100) if required else 100
        missing_required = len(answered) < len(required)
        checklist.completeness_score = score
        checklist.quote_ready = (
            score >= self.settings.phase13_scope_completeness_quote_threshold
            and not missing_required
        )
        checklist.proposal_ready = checklist.quote_ready
        checklist.status = (
            ChecklistStatus.COMPLETED
            if score == 100
            else ChecklistStatus.PARTIAL
            if score > 0
            else ChecklistStatus.OPEN
        )
        return score
