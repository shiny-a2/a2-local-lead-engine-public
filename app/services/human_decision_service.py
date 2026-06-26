from sqlalchemy.orm import Session

from app.core.enums import (
    FinalPreSendCheckStatus,
    HumanReviewAuditAction,
    HumanReviewDecisionValue,
    HumanReviewQueueStatus,
    Phase9Decision,
)
from app.db.models.human_review_audit_event import HumanReviewAuditEvent
from app.db.models.human_review_decision import HumanReviewDecision
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.db.models.phase9_candidate_decision import Phase9CandidateDecision
from app.services.final_pre_send_review_service import FinalPreSendReviewService
from app.settings import Settings


class HumanDecisionService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def approve(self, queue_item_id: int, reviewer: str, notes: str | None = None) -> HumanReviewDecision:
        item = self._item(queue_item_id)
        check = FinalPreSendReviewService(self.session, self.settings).run(queue_item_id, manual_approval=True)
        if check.check_status == FinalPreSendCheckStatus.FAILED:
            item.queue_status = HumanReviewQueueStatus.BLOCKED_BY_FINAL_PRE_SEND_CHECK
            self.session.add(HumanReviewAuditEvent(queue_item_id=item.id, actor=reviewer, action=HumanReviewAuditAction.FINAL_CHECK_FAILED, reason="final pre-send check failed"))
            return self._decision(item, HumanReviewDecisionValue.BLOCKED_BY_FINAL_PRE_SEND_CHECK, reviewer, "final pre-send check failed", notes)
        decision = (
            HumanReviewDecisionValue.APPROVED_WITH_MINOR_WARNINGS_FOR_PHASE_10
            if check.check_status == FinalPreSendCheckStatus.PASSED_WITH_WARNINGS
            else HumanReviewDecisionValue.APPROVED_FOR_PHASE_10_SEND_QUEUE
        )
        item.queue_status = (
            HumanReviewQueueStatus.APPROVED_WITH_WARNINGS_FOR_PHASE10
            if decision == HumanReviewDecisionValue.APPROVED_WITH_MINOR_WARNINGS_FOR_PHASE_10
            else HumanReviewQueueStatus.APPROVED_FOR_PHASE10
        )
        self.session.add(HumanReviewAuditEvent(queue_item_id=item.id, actor=reviewer, action=HumanReviewAuditAction.APPROVED_FOR_PHASE10, reason=notes))
        return self._decision(item, decision, reviewer, "approved for Phase 10 controlled queue only", notes)

    def reject(self, queue_item_id: int, reviewer: str, reason: str) -> HumanReviewDecision:
        self._require_reason(reason)
        item = self._item(queue_item_id)
        item.queue_status = HumanReviewQueueStatus.REJECTED
        self.session.add(HumanReviewAuditEvent(queue_item_id=item.id, actor=reviewer, action=HumanReviewAuditAction.REJECTED, reason=reason))
        return self._decision(item, HumanReviewDecisionValue.REJECTED_BY_HUMAN, reviewer, reason)

    def hold(self, queue_item_id: int, reviewer: str, reason: str) -> HumanReviewDecision:
        self._require_reason(reason)
        item = self._item(queue_item_id)
        item.queue_status = HumanReviewQueueStatus.HELD
        self.session.add(HumanReviewAuditEvent(queue_item_id=item.id, actor=reviewer, action=HumanReviewAuditAction.HELD, reason=reason))
        return self._decision(item, HumanReviewDecisionValue.HOLD_FOR_LATER, reviewer, reason)

    def return_rewrite(self, queue_item_id: int, reviewer: str, reason: str) -> HumanReviewDecision:
        self._require_reason(reason)
        item = self._item(queue_item_id)
        item.queue_status = HumanReviewQueueStatus.RETURNED_TO_PHASE7_REWRITE
        self.session.add(HumanReviewAuditEvent(queue_item_id=item.id, actor=reviewer, action=HumanReviewAuditAction.RETURNED_TO_REWRITE, reason=reason))
        return self._decision(item, HumanReviewDecisionValue.RETURN_TO_PHASE_7_REWRITE, reviewer, reason)

    def return_judge(self, queue_item_id: int, reviewer: str, reason: str) -> HumanReviewDecision:
        self._require_reason(reason)
        item = self._item(queue_item_id)
        item.queue_status = HumanReviewQueueStatus.RETURNED_TO_PHASE8_REJUDGE
        self.session.add(HumanReviewAuditEvent(queue_item_id=item.id, actor=reviewer, action=HumanReviewAuditAction.RETURNED_TO_JUDGE, reason=reason))
        return self._decision(item, HumanReviewDecisionValue.RETURN_TO_PHASE_8_REJUDGE, reviewer, reason)

    def _decision(self, item: HumanReviewQueueItem, decision: HumanReviewDecisionValue, reviewer: str, reason: str, notes: str | None = None) -> HumanReviewDecision:
        row = HumanReviewDecision(human_review_run_id=item.human_review_run_id, queue_item_id=item.id, candidate_business_id=item.candidate_business_id, email_draft_variant_id=item.email_draft_variant_id, decision=decision, reviewer=reviewer, reason=reason, notes=notes)
        phase9 = self._phase9_decision(item, decision, reason)
        self.session.add(row)
        self.session.add(phase9)
        self.session.flush()
        return row

    def _phase9_decision(self, item: HumanReviewQueueItem, decision: HumanReviewDecisionValue, reason: str) -> Phase9CandidateDecision:
        mapping = {
            HumanReviewDecisionValue.APPROVED_FOR_PHASE_10_SEND_QUEUE: Phase9Decision.READY_FOR_PHASE_10_CONTROLLED_SEND_QUEUE,
            HumanReviewDecisionValue.APPROVED_WITH_MINOR_WARNINGS_FOR_PHASE_10: Phase9Decision.READY_FOR_PHASE_10_WITH_WARNINGS,
            HumanReviewDecisionValue.RETURN_TO_PHASE_7_REWRITE: Phase9Decision.RETURN_TO_PHASE_7_REWRITE,
            HumanReviewDecisionValue.RETURN_TO_PHASE_8_REJUDGE: Phase9Decision.RETURN_TO_PHASE_8_REJUDGE,
            HumanReviewDecisionValue.HOLD_FOR_LATER: Phase9Decision.HOLD_FOR_LATER,
            HumanReviewDecisionValue.REJECTED_BY_HUMAN: Phase9Decision.REJECTED_BY_HUMAN,
            HumanReviewDecisionValue.BLOCKED_BY_FINAL_PRE_SEND_CHECK: Phase9Decision.BLOCKED_BY_FINAL_PRE_SEND_CHECK,
        }
        phase9_decision = mapping.get(decision, Phase9Decision.NEEDS_MANUAL_EDIT)
        return Phase9CandidateDecision(candidate_business_id=item.candidate_business_id, human_review_run_id=item.human_review_run_id, queue_item_id=item.id, decision=phase9_decision, ready_for_phase10=phase9_decision in {Phase9Decision.READY_FOR_PHASE_10_CONTROLLED_SEND_QUEUE, Phase9Decision.READY_FOR_PHASE_10_WITH_WARNINGS}, manual_edit_required=phase9_decision == Phase9Decision.NEEDS_MANUAL_EDIT, blocked=phase9_decision == Phase9Decision.BLOCKED_BY_FINAL_PRE_SEND_CHECK, hold_reason=reason if phase9_decision == Phase9Decision.HOLD_FOR_LATER else None, reject_reason=reason if phase9_decision in {Phase9Decision.REJECTED_BY_HUMAN, Phase9Decision.BLOCKED_BY_FINAL_PRE_SEND_CHECK} else None)

    def _item(self, queue_item_id: int) -> HumanReviewQueueItem:
        item = self.session.get(HumanReviewQueueItem, queue_item_id)
        if item is None:
            raise ValueError("queue item not found")
        return item

    def _require_reason(self, reason: str) -> None:
        if not reason:
            raise ValueError("reason required")
