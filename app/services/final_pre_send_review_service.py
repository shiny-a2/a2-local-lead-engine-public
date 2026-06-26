from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import EmailJudgeDecisionValue, FinalPreSendCheckStatus, ManualEditSeverity
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.email_manual_edit_version import EmailManualEditVersion
from app.db.models.final_pre_send_check import FinalPreSendCheck
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.services.contact_finalization_service import ContactFinalizationService
from app.services.mailbox_readiness_service import MailboxReadinessService
from app.services.sender_identity_readiness_service import SenderIdentityReadinessService
from app.services.suppression_check_service import SuppressionCheckService
from app.settings import Settings


class FinalPreSendReviewService:
    unsafe_terms = ["you don't have a website", "guaranteed", "stop paying commissions", "google maps"]

    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def run(self, queue_item_id: int, manual_approval: bool = True) -> FinalPreSendCheck:
        item = self.session.get(HumanReviewQueueItem, queue_item_id)
        if item is None:
            raise ValueError("queue item not found")
        draft = self.session.get(EmailDraftVariant, item.email_draft_variant_id)
        if draft is None:
            raise ValueError("draft not found")
        version = self.session.scalar(
            select(EmailManualEditVersion)
            .where(EmailManualEditVersion.queue_item_id == queue_item_id)
            .order_by(EmailManualEditVersion.version_number.desc())
        )
        subject = version.subject_text if version else draft.subject_text
        body = version.body_text if version else draft.body_text
        text = f"{subject}\n{body}".lower()
        flags: list[str] = []
        sender_ok, sender_notes, profile = SenderIdentityReadinessService(self.session, self.settings).readiness()
        mailbox = MailboxReadinessService(self.session, self.settings).record(profile)
        recipient, contact_ok, contact_flags = ContactFinalizationService(self.session).final_email(item.candidate_business_id)
        suppression_ok, suppression_flags = SuppressionCheckService(self.session).check(recipient)
        claim_ok = not any(term in text for term in self.unsafe_terms)
        unsubscribe_ok = (not self.settings.phase9_require_unsubscribe_placeholder) or self.settings.email_unsubscribe_placeholder in body
        body_length_ok = self.settings.email_min_words <= len(body.split()) <= self.settings.email_max_words
        subject_ok = len(subject.split()) <= self.settings.email_max_subject_words and "urgent" not in subject.lower()
        single_cta_ok = body.count("?") <= 1
        judge = self.session.scalar(
            select(EmailJudgeDecision)
            .where(EmailJudgeDecision.email_draft_variant_id == draft.id)
            .order_by(EmailJudgeDecision.id.desc())
        )
        judge_validity_ok = bool(
            judge
            and judge.decision
            in {
                EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW,
                EmailJudgeDecisionValue.APPROVED_WITH_WARNINGS_FOR_HUMAN_REVIEW,
            }
        )
        if version and version.requires_rejudge:
            judge_validity_ok = False
            flags.append(f"edit_requires_rejudge:{version.edit_severity.value}")
        if version and version.edit_severity == ManualEditSeverity.MODERATE:
            flags.append("moderate_edit_not_rejudged")
        flags.extend(sender_notes)
        flags.extend(contact_flags)
        flags.extend(suppression_flags)
        if not claim_ok:
            flags.append("unsafe_claim")
        if not unsubscribe_ok:
            flags.append("missing_unsubscribe_placeholder")
        if not sender_ok:
            flags.append("missing_sender_identity")
        if not single_cta_ok:
            flags.append("multiple_cta")
        if mailbox.readiness_status.value in {"NOT_CONFIGURED", "FUTURE_PHASE_REQUIRED"}:
            flags.append("mailbox_readiness_future_phase")
        blockers = [
            suppression_ok,
            claim_ok,
            unsubscribe_ok,
            sender_ok,
            contact_ok,
            single_cta_ok,
            judge_validity_ok,
            manual_approval,
        ]
        status = FinalPreSendCheckStatus.FAILED if not all(blockers) else FinalPreSendCheckStatus.PASSED_WITH_WARNINGS if flags else FinalPreSendCheckStatus.PASSED
        row = FinalPreSendCheck(
            queue_item_id=item.id,
            candidate_business_id=item.candidate_business_id,
            email_manual_edit_version_id=version.id if version else None,
            email_draft_variant_id=draft.id,
            check_status=status,
            sender_identity_ok=sender_ok,
            unsubscribe_placeholder_ok=unsubscribe_ok,
            recipient_contact_ok=contact_ok,
            suppression_ok=suppression_ok,
            claim_safety_ok=claim_ok,
            body_length_ok=body_length_ok,
            subject_ok=subject_ok,
            single_cta_ok=single_cta_ok,
            judge_validity_ok=judge_validity_ok,
            staleness_ok=True,
            manual_approval_ok=manual_approval,
            mailbox_readiness_ok=mailbox.readiness_status.value != "NOT_CONFIGURED",
            risk_flags_json=flags,
        )
        self.session.add(row)
        self.session.flush()
        return row
