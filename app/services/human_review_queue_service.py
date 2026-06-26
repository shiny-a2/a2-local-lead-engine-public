from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    EmailJudgeDecisionValue,
    HumanReviewAuditAction,
    HumanReviewOperation,
    HumanReviewQueueStatus,
    HumanReviewRunStatus,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.email_judge_run import EmailJudgeRun
from app.db.models.human_review_audit_event import HumanReviewAuditEvent
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.models.human_review_run import HumanReviewRun
from app.settings import Settings


class HumanReviewQueueService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def eligible(self, judge_run_id: str | None = None) -> list[EmailJudgeDecision]:
        query = select(EmailJudgeDecision).where(
            EmailJudgeDecision.ready_for_phase9.is_(True),
            EmailJudgeDecision.decision.in_(
                [
                    EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW,
                    EmailJudgeDecisionValue.APPROVED_WITH_WARNINGS_FOR_HUMAN_REVIEW,
                ]
            ),
        )
        if judge_run_id:
            run = self.session.scalar(select(EmailJudgeRun).where(EmailJudgeRun.run_id == judge_run_id))
            if run is None:
                return []
            query = query.where(EmailJudgeDecision.email_judge_run_id == run.id)
        return list(self.session.scalars(query.order_by(EmailJudgeDecision.id)).all())

    def build_queue(self, campaign_slug: str, judge_run_id: str | None, commit: bool) -> HumanReviewRun:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        decisions = self.eligible(judge_run_id)[: self.settings.phase9_max_queue_items_per_run]
        run = HumanReviewRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation=HumanReviewOperation.BUILD_HUMAN_REVIEW_QUEUE,
            status=HumanReviewRunStatus.STARTED,
            dry_run=not commit,
            input_draft_count=len(decisions),
            metadata_json={"email_sent": False, "scheduled": False, "smtp": "not-implemented"},
        )
        self.session.add(run)
        self.session.flush()
        queued = 0
        if not decisions:
            run.status = HumanReviewRunStatus.BLOCKED_BY_NO_ELIGIBLE_DRAFTS
        elif not commit:
            run.status = HumanReviewRunStatus.DRY_RUN_ONLY
        else:
            for decision in decisions:
                draft = self.session.get(EmailDraftVariant, decision.email_draft_variant_id)
                if draft is None:
                    continue
                existing = self.session.scalar(
                    select(HumanReviewQueueItem).where(
                        HumanReviewQueueItem.email_draft_variant_id == draft.id
                    )
                )
                if existing:
                    continue
                item = HumanReviewQueueItem(
                    human_review_run_id=run.id,
                    candidate_business_id=decision.candidate_business_id,
                    email_draft_variant_id=draft.id,
                    phase8_decision_id=decision.id,
                    queue_status=HumanReviewQueueStatus.QUEUED,
                    campaign_lane=draft.campaign_lane,
                )
                self.session.add(item)
                self.session.flush()
                self.session.add(HumanReviewAuditEvent(queue_item_id=item.id, actor="cli", action=HumanReviewAuditAction.QUEUED))
                queued += 1
            run.queued_count = queued
            run.status = HumanReviewRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        self.session.commit()
        return run
