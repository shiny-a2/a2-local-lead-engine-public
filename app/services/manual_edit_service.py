from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import HumanReviewAuditAction, HumanReviewQueueStatus, ManualEditSeverity
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_manual_edit_version import EmailManualEditVersion
from app.db.models.human_review_audit_event import HumanReviewAuditEvent
from app.db.models.human_review_queue_item import HumanReviewQueueItem
from app.settings import Settings


class ManualEditService:
    risky_claim_terms = ["guaranteed", "save thousands", "stop paying commissions", "you don't have a website"]
    economic_terms = ["commission", "savings", "guaranteed", "replace"]

    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def create_version(self, queue_item_id: int, subject: str, body: str, editor: str, reason: str) -> EmailManualEditVersion:
        if not reason:
            raise ValueError("edit reason required")
        item = self.session.get(HumanReviewQueueItem, queue_item_id)
        if item is None:
            raise ValueError("queue item not found")
        draft = self.session.get(EmailDraftVariant, item.email_draft_variant_id)
        if draft is None:
            raise ValueError("draft not found")
        previous = self.session.scalar(
            select(EmailManualEditVersion)
            .where(EmailManualEditVersion.queue_item_id == queue_item_id)
            .order_by(EmailManualEditVersion.version_number.desc())
        )
        base_subject = previous.subject_text if previous else draft.subject_text
        base_body = previous.body_text if previous else draft.body_text
        severity, requires_rejudge = self._severity(base_subject, base_body, subject, body)
        version = EmailManualEditVersion(
            queue_item_id=queue_item_id,
            candidate_business_id=item.candidate_business_id,
            original_email_draft_variant_id=draft.id,
            previous_version_id=previous.id if previous else None,
            version_number=(previous.version_number + 1) if previous else 1,
            subject_text=subject,
            body_text=body,
            editor=editor,
            edit_reason=reason,
            diff_json={"old_subject": base_subject, "new_subject": subject, "old_words": len(base_body.split()), "new_words": len(body.split())},
            edit_severity=severity,
            requires_rejudge=requires_rejudge,
        )
        item.queue_status = HumanReviewQueueStatus.REJUDGE_REQUIRED if requires_rejudge else HumanReviewQueueStatus.EDITED_NEEDS_CHECK
        self.session.add(version)
        self.session.add(HumanReviewAuditEvent(queue_item_id=queue_item_id, actor=editor, action=HumanReviewAuditAction.EDITED, reason=reason))
        self.session.flush()
        return version

    def _severity(self, old_subject: str, old_body: str, new_subject: str, new_body: str) -> tuple[ManualEditSeverity, bool]:
        lowered = new_body.lower()
        if any(term in lowered for term in self.risky_claim_terms):
            return ManualEditSeverity.NEW_CLAIM_DETECTED, True
        if any(term in lowered for term in self.economic_terms) and lowered != old_body.lower():
            return ManualEditSeverity.ECONOMIC_WORDING_CHANGED, True
        if old_body.count("?") != new_body.count("?"):
            return ManualEditSeverity.CTA_CHANGED, False
        similarity = SequenceMatcher(None, old_body, new_body).ratio()
        changed = int((1 - similarity) * 100)
        if changed > self.settings.phase9_major_edit_percent_threshold:
            return ManualEditSeverity.MAJOR, True
        if changed >= self.settings.phase9_minor_edit_percent_threshold:
            return ManualEditSeverity.MODERATE, False
        if old_subject != new_subject:
            return ManualEditSeverity.MINOR, False
        return ManualEditSeverity.MINOR if changed else ManualEditSeverity.NONE, False
