from sqlalchemy.orm import Session

from app.core.enums import ReplyDraftGenerationMode, ReplyDraftSuggestionStatus
from app.db.models.opportunity_record import OpportunityRecord
from app.db.models.reply_draft_suggestion import ReplyDraftSuggestion
from app.settings import Settings


class ReplyDraftSuggestionService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create_optional(self, opportunity: OpportunityRecord) -> ReplyDraftSuggestion | None:
        if not self.settings.phase12_allow_reply_draft_suggestions:
            return None
        status = (
            ReplyDraftSuggestionStatus.NEEDS_HUMAN_EDIT
            if self.settings.phase12_reply_drafts_internal_only
            else ReplyDraftSuggestionStatus.BLOCKED_BY_POLICY
        )
        row = ReplyDraftSuggestion(
            opportunity_id=opportunity.id,
            inbound_message_id=opportunity.source_inbound_message_id,
            draft_subject=None,
            draft_body="Internal guidance suggestion only. Human must rewrite before any use.",
            generation_mode=ReplyDraftGenerationMode.RULE_TEMPLATE,
            status=status,
            risk_flags_json={"internal_only": True, "send_ready": False},
        )
        self.session.add(row)
        self.session.flush()
        return row
