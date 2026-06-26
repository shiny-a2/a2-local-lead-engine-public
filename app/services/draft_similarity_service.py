from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import DraftSimilarityDecision
from app.db.models.email_draft_similarity_result import EmailDraftSimilarityResult
from app.db.models.email_draft_variant import EmailDraftVariant
from app.settings import Settings


class DraftSimilarityService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def compare(self, draft: EmailDraftVariant) -> EmailDraftSimilarityResult:
        existing = self.session.scalar(
            select(EmailDraftVariant)
            .where(
                EmailDraftVariant.email_generation_run_id == draft.email_generation_run_id,
                EmailDraftVariant.id != draft.id,
            )
            .order_by(EmailDraftVariant.id.desc())
        )
        score = 0.0
        compared = None
        if existing is not None:
            compared = existing.id
            score = SequenceMatcher(None, existing.body_text, draft.body_text).ratio()
        decision = DraftSimilarityDecision.OK
        if score > self.settings.email_max_similarity_score:
            decision = DraftSimilarityDecision.BLOCKED_TOO_SIMILAR
        elif score > 0.7:
            decision = DraftSimilarityDecision.WARNING_SIMILAR
        return EmailDraftSimilarityResult(
            email_draft_variant_id=draft.id,
            compared_against_draft_id=compared,
            similarity_score=round(score, 3),
            repeated_phrases_json=[],
            decision=decision,
        )
