from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import EmailJudgeDecisionValue
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.email_variant_selection import EmailVariantSelection


class VariantSelectionService:
    def __init__(self, session: Session):
        self.session = session

    def select_for_run(self, run_id: int) -> list[EmailVariantSelection]:
        decisions = self.session.scalars(
            select(EmailJudgeDecision).where(EmailJudgeDecision.email_judge_run_id == run_id)
        ).all()
        by_candidate: dict[int, list[EmailJudgeDecision]] = {}
        for decision in decisions:
            by_candidate.setdefault(decision.candidate_business_id, []).append(decision)
        selections: list[EmailVariantSelection] = []
        for candidate_id, rows in by_candidate.items():
            passing = [
                row
                for row in rows
                if row.decision
                in {
                    EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW,
                    EmailJudgeDecisionValue.APPROVED_WITH_WARNINGS_FOR_HUMAN_REVIEW,
                }
            ]
            passing.sort(key=lambda row: row.quality_score, reverse=True)
            rejected = [row.email_draft_variant_id for row in rows if row not in passing]
            selection = EmailVariantSelection(
                email_judge_run_id=run_id,
                candidate_business_id=candidate_id,
                preferred_email_draft_variant_id=passing[0].email_draft_variant_id if passing else None,
                backup_email_draft_variant_id=passing[1].email_draft_variant_id if len(passing) > 1 else None,
                selection_reason="Highest quality passing variant selected." if passing else "No passing variant.",
                rejected_variant_ids_json=rejected,
            )
            if passing:
                passing[0].preferred_variant = True
            selections.append(selection)
        return selections
