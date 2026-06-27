from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    EmailSendQueueStatus,
    Phase9Decision,
    Phase10Decision,
    SendAuditAction,
    SendQueueOperation,
    SendQueueRunStatus,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.final_pre_send_check import FinalPreSendCheck
from app.db.models.phase9_candidate_decision import Phase9CandidateDecision
from app.db.models.phase10_candidate_decision import Phase10CandidateDecision
from app.db.models.send_audit_event import SendAuditEvent
from app.db.models.send_queue_run import SendQueueRun
from app.services.duplicate_send_guard_service import DuplicateSendGuardService
from app.services.provider_readiness_service import ProviderReadinessService
from app.settings import Settings


class SendQueueService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings

    def build_queue(self, campaign_slug: str, human_review_run_id: str | None, commit: bool) -> SendQueueRun:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        decisions = self.session.scalars(select(Phase9CandidateDecision).where(Phase9CandidateDecision.ready_for_phase10.is_(True), Phase9CandidateDecision.decision.in_([Phase9Decision.READY_FOR_PHASE_10_CONTROLLED_SEND_QUEUE, Phase9Decision.READY_FOR_PHASE_10_WITH_WARNINGS]))).all()
        run = SendQueueRun(run_id=RunContext().run_id, campaign_id=campaign.id, operation=SendQueueOperation.BUILD_SEND_QUEUE, status=SendQueueRunStatus.STARTED, dry_run=not commit, input_approved_count=len(decisions), metadata_json={"email_sent": False, "dry_run": not commit})
        self.session.add(run)
        self.session.flush()
        provider_ok, _, provider = ProviderReadinessService(self.session, self.settings).check()
        queued = 0
        blocked = 0
        guard = DuplicateSendGuardService(self.session)
        for decision in decisions:
            check = self.session.scalar(select(FinalPreSendCheck).where(FinalPreSendCheck.queue_item_id == decision.queue_item_id).order_by(FinalPreSendCheck.id.desc()))
            if not check or check.check_status.value == "FAILED":
                blocked += 1
                continue
            recipient_email = self._recipient_email(decision.candidate_business_id)
            if not recipient_email:
                blocked += 1  # no safe verified contact -> cannot send
                continue
            domain = recipient_email.split("@")[-1].lower()
            key = guard.idempotency_key(campaign.id, decision.candidate_business_id, recipient_email)
            duplicate_ok, _ = guard.check(key)
            if not duplicate_ok:
                blocked += 1
                continue
            if commit:
                item = EmailSendQueue(send_queue_run_id=run.id, campaign_id=campaign.id, candidate_business_id=decision.candidate_business_id, phase9_decision_id=decision.id, email_draft_variant_id=self._draft_id(decision.queue_item_id), email_manual_edit_version_id=check.email_manual_edit_version_id, recipient_email=recipient_email, recipient_domain=domain, sender_profile_id=provider.id, idempotency_key=key, queue_status=EmailSendQueueStatus.READY_TO_SEND_CONTROLLED if provider_ok else EmailSendQueueStatus.BLOCKED_BY_PROVIDER_CONFIG, max_retries=self.settings.send_max_retries)
                self.session.add(item)
                self.session.flush()
                self.session.add(SendAuditEvent(email_send_queue_id=item.id, actor="cli", action=SendAuditAction.QUEUE_CREATED))
                self.session.add(Phase10CandidateDecision(candidate_business_id=decision.candidate_business_id, send_queue_run_id=run.id, email_send_queue_id=item.id, decision=Phase10Decision.QUEUED_FOR_CONTROLLED_SEND if provider_ok else Phase10Decision.BLOCKED_BY_PROVIDER_CONFIG, blocked=not provider_ok, reason="Queued for controlled sending only." if provider_ok else "Provider config incomplete."))
            queued += int(provider_ok)
        run.queued_count = queued if commit else 0
        run.blocked_count = blocked
        run.status = SendQueueRunStatus.DRY_RUN_ONLY if not commit else SendQueueRunStatus.COMPLETED_WITH_WARNINGS if blocked else SendQueueRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        self.session.commit()
        return run

    def _draft_id(self, queue_item_id: int) -> int:
        from app.db.models.human_review_queue_item import HumanReviewQueueItem

        item = self.session.get(HumanReviewQueueItem, queue_item_id)
        if item is None:
            raise ValueError("phase9 queue item not found")
        return item.email_draft_variant_id

    def _recipient_email(self, candidate_business_id: int) -> str | None:
        """The candidate's verified, outreach-allowed contact email (no placeholder)."""
        from app.db.models.candidate_contact_verification import CandidateContactVerification

        contact = self.session.scalar(
            select(CandidateContactVerification)
            .where(
                CandidateContactVerification.candidate_business_id == candidate_business_id,
                CandidateContactVerification.outreach_contact_allowed.is_(True),
            )
            .order_by(CandidateContactVerification.id.desc())
        )
        return contact.best_email if contact and contact.best_email else None
