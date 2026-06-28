from datetime import UTC, datetime
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    EmailDraftVariantStatus,
    EmailProviderType,
    EmailSendQueueStatus,
    Phase10Decision,
    ProviderStatus,
    SendAttemptStatus,
    SendAuditAction,
    SendQueueOperation,
    SendQueueRunStatus,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_send_attempt import EmailSendAttempt
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.phase10_candidate_decision import Phase10CandidateDecision
from app.db.models.send_audit_event import SendAuditEvent
from app.db.models.send_queue_run import SendQueueRun
from app.services.country_compliance_service import CountryComplianceService
from app.services.cpanel_smtp_provider import CpanelSmtpProvider
from app.services.list_unsubscribe_header_service import ListUnsubscribeHeaderService
from app.services.message_snapshot_service import MessageSnapshotService
from app.services.null_dry_run_provider import NullDryRunProvider
from app.services.provider_circuit_breaker_service import ProviderCircuitBreakerService
from app.services.provider_readiness_service import ProviderReadinessService
from app.services.provider_response_normalizer import ProviderResponseNormalizer
from app.services.send_limit_service import CooldownGuardService, SendLimitService
from app.services.send_window_service import SendWindowService
from app.services.suppression_enforcement_service import SuppressionEnforcementService
from app.services.transactional_send_lock_service import TransactionalSendLockService
from app.services.unsubscribe_token_service import UnsubscribeTokenService
from app.settings import Settings


class ControlledSendService:
    def __init__(self, session: Session, settings: Settings, provider=None):
        self.session = session
        self.settings = settings
        self.provider = provider

    def run(self, campaign_slug: str, limit: int, commit: bool) -> SendQueueRun:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        items = self.session.scalars(
            select(EmailSendQueue)
            .where(EmailSendQueue.campaign_id == campaign.id)
            .where(EmailSendQueue.queue_status == EmailSendQueueStatus.READY_TO_SEND_CONTROLLED)
            .order_by(EmailSendQueue.id)
            .limit(limit)
        ).all()
        run = SendQueueRun(run_id=RunContext().run_id, campaign_id=campaign.id, operation=SendQueueOperation.CONTROLLED_SEND, status=SendQueueRunStatus.STARTED, dry_run=not commit, input_approved_count=len(items), metadata_json={"provider_call_attempted": False, "followups": "not-implemented"})
        self.session.add(run)
        self.session.flush()
        if self.settings.global_outreach_kill_switch and commit:
            run.status = SendQueueRunStatus.BLOCKED_BY_GLOBAL_KILL_SWITCH
            self._block_all(items, run, Phase10Decision.BLOCKED_BY_GLOBAL_KILL_SWITCH, EmailSendQueueStatus.BLOCKED_BY_GLOBAL_KILL_SWITCH, "global kill switch enabled")
        elif not commit:
            for item in items:
                self._dry_plan(item)
            run.status = SendQueueRunStatus.DRY_RUN_ONLY
        else:
            for item in items:
                self._send_one(run, item)
            run.status = SendQueueRunStatus.COMPLETED_WITH_WARNINGS if run.blocked_count or run.failed_count else SendQueueRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        self.session.commit()
        return run

    def _send_one(self, run: SendQueueRun, item: EmailSendQueue) -> None:
        if not (self.settings.email_sending_enabled and self.settings.controlled_send_enabled and self.settings.provider_send_enabled):
            self._block(item, run, Phase10Decision.BLOCKED_BY_GLOBAL_KILL_SWITCH, EmailSendQueueStatus.BLOCKED_BY_GLOBAL_KILL_SWITCH, "send flags disabled")
            return
        circuit = ProviderCircuitBreakerService(self.session, self.settings)
        circuit_ok, _ = circuit.can_send(self.settings.email_provider_slug)
        if not circuit_ok:
            self._block(item, run, Phase10Decision.BLOCKED_BY_PROVIDER_CIRCUIT_BREAKER, EmailSendQueueStatus.BLOCKED_BY_PROVIDER_CIRCUIT_BREAKER, "provider circuit open")
            return
        if not TransactionalSendLockService(self.session).claim(item):
            self._block(item, run, Phase10Decision.HELD_FOR_MANUAL_SEND_REVIEW, EmailSendQueueStatus.HELD_BY_OPERATOR, "could not claim queue item")
            return
        provider_ok, provider_gaps, provider_config = ProviderReadinessService(self.session, self.settings).check()
        if not provider_ok:
            self._block(item, run, Phase10Decision.BLOCKED_BY_PROVIDER_CONFIG, EmailSendQueueStatus.BLOCKED_BY_PROVIDER_CONFIG, ";".join(provider_gaps))
            return
        suppression_ok, suppression_flags = SuppressionEnforcementService(self.session).check_queue_item(item)
        if not suppression_ok:
            self._block(item, run, Phase10Decision.BLOCKED_BY_SUPPRESSION, EmailSendQueueStatus.BLOCKED_BY_SUPPRESSION, ";".join(suppression_flags))
            return
        if self.settings.country_compliance_enforced:
            candidate = self.session.get(CandidateBusiness, item.candidate_business_id)
            compliance = CountryComplianceService().evaluate(candidate.country if candidate else None)
            if not compliance["allowed"]:
                self._block(item, run, Phase10Decision.BLOCKED_BY_COUNTRY_COMPLIANCE, EmailSendQueueStatus.BLOCKED_BY_COUNTRY_COMPLIANCE, compliance["block_reason"] or "country requires opt-in consent")
                return
        limits_ok, limit_flags = SendLimitService(self.session, self.settings).check(run.id, item.recipient_domain)
        if not limits_ok:
            self._block(item, run, Phase10Decision.BLOCKED_BY_DAILY_LIMIT, EmailSendQueueStatus.BLOCKED_BY_DAILY_LIMIT, ";".join(limit_flags))
            return
        cooldown_ok, cooldown_flags = CooldownGuardService(self.session, self.settings).check(item.recipient_email, item.candidate_business_id, item.campaign_id)
        if not cooldown_ok:
            self._block(item, run, Phase10Decision.BLOCKED_DUPLICATE_SEND, EmailSendQueueStatus.BLOCKED_DUPLICATE_SEND, ";".join(cooldown_flags))
            return
        window_ok, window_reason = SendWindowService(self.settings).check()
        if not window_ok:
            self._block(item, run, Phase10Decision.BLOCKED_BY_SEND_WINDOW, EmailSendQueueStatus.BLOCKED_BY_SEND_WINDOW, window_reason)
            return
        token, raw = UnsubscribeTokenService(self.session, self.settings).create(item.campaign_id, item.candidate_business_id, item.recipient_email, item.id)
        item.unsubscribe_token_id = token.id
        unsubscribe_url = UnsubscribeTokenService(self.session, self.settings).url(raw)
        from_email = provider_config.from_email
        # The body opt-out is reply/mailto based so it works WITHOUT a deployed web endpoint;
        # the token URL still rides in the List-Unsubscribe header for when the page is live.
        body_optout = (
            f"To stop receiving these emails, reply to this message with the word UNSUBSCRIBE, "
            f"or email {from_email} with the subject Unsubscribe and you will be removed."
        )
        snapshot = MessageSnapshotService(self.session, self.settings).create(item, provider_config, body_optout)
        message = self._message(provider_config, item.recipient_email, snapshot.final_subject_snapshot, snapshot.final_body_snapshot, unsubscribe_url, from_email)
        if self.settings.pre_send_qa_enabled:
            from app.services.pre_send_qa_service import PreSendQaService

            cand = self.session.get(CandidateBusiness, item.candidate_business_id)
            qa = PreSendQaService(self.settings).check(
                cand.display_name if cand else "", cand.city if cand else None,
                cand.country if cand else None, item.recipient_email,
                snapshot.final_subject_snapshot, snapshot.final_body_snapshot,
            )
            if not qa["go"]:
                # Classify WHY: a TEXT problem routes the draft into the rewrite loop; a CONTACT
                # problem (wrong recipient) must NOT be reworded-and-resent — it stays held.
                from app.services.rejection_taxonomy_service import RejectionTaxonomyService

                bucket = RejectionTaxonomyService().classify_qa(qa["issues"])
                draft = self.session.get(EmailDraftVariant, item.email_draft_variant_id)
                text_fixable = (
                    bucket == "TEXT_FIXABLE"
                    and self.settings.email_rewrite_enabled
                    and draft is not None
                    and draft.rewrite_attempt < self.settings.email_rewrite_max_attempts
                )
                if text_fixable:
                    draft.status = EmailDraftVariantStatus.AWAITING_REWRITE
                tag = "QA_TEXT_FIXABLE" if text_fixable else "QA_CONTACT_FIXABLE"
                self._block(item, run, Phase10Decision.HELD_FOR_MANUAL_SEND_REVIEW, EmailSendQueueStatus.HELD_BY_OPERATOR, f"{tag}: " + "; ".join(qa["issues"])[:240])
                return
        provider = self.provider or self._provider()
        run.metadata_json = {**(run.metadata_json or {}), "provider_call_attempted": True}
        result = provider.send(message, dry_run=False)
        attempt_status = ProviderResponseNormalizer().attempt_status(result)
        self.session.add(EmailSendAttempt(email_send_queue_id=item.id, provider_type=result.provider_type, provider_message_id=result.provider_message_id, smtp_response_code=result.smtp_response_code, provider_status=result.provider_status, attempt_status=attempt_status, attempt_number=item.retry_count + 1, error_type=result.error_type, error_message=result.error_message, transient_error=result.transient_error, permanent_error=result.permanent_error, sent_at=datetime.now(UTC) if attempt_status == SendAttemptStatus.SENT_TO_PROVIDER else None))
        if result.provider_status == ProviderStatus.ACCEPTED:
            item.queue_status = EmailSendQueueStatus.SENT_TO_PROVIDER
            run.sent_count += 1
            SendLimitService(self.session, self.settings).increment(run.id, item.recipient_domain)
            circuit.record_success(self.settings.email_provider_slug)
            decision = Phase10Decision.SENT_TO_PROVIDER
            sent = True
        else:
            item.queue_status = EmailSendQueueStatus.FAILED_SMTP_ERROR if attempt_status == SendAttemptStatus.FAILED_SMTP_ERROR else EmailSendQueueStatus.FAILED_PROVIDER_ERROR
            run.failed_count += 1
            circuit.record_failure(self.settings.email_provider_slug, result.error_type or "provider_error")
            decision = Phase10Decision.FAILED_SEND_ATTEMPT
            sent = False
        run.send_attempted_count += 1
        self.session.add(Phase10CandidateDecision(candidate_business_id=item.candidate_business_id, send_queue_run_id=run.id, email_send_queue_id=item.id, decision=decision, sent=sent, blocked=not sent, reason="SMTP accepted message; delivery unknown." if sent else "provider failure"))
        self.session.add(SendAuditEvent(email_send_queue_id=item.id, actor="cli", action=SendAuditAction.SENT_TO_PROVIDER if sent else SendAuditAction.SEND_FAILED))
        self.session.flush()

    def _message(self, provider_config, recipient: str, subject: str, body: str, unsubscribe_url: str, mailto_email: str | None = None) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = f"{provider_config.from_name} <{provider_config.from_email}>"
        msg["To"] = recipient
        msg["Reply-To"] = provider_config.reply_to_email
        msg["Subject"] = subject
        ListUnsubscribeHeaderService().add(
            msg, unsubscribe_url, mailto_email, self.settings.unsubscribe_one_click_enabled
        )
        msg.set_content(body)
        return msg

    def _provider(self):
        if self.settings.email_provider == EmailProviderType.NULL_DRY_RUN.value:
            return NullDryRunProvider()
        return CpanelSmtpProvider(self.settings)

    def _dry_plan(self, item: EmailSendQueue) -> None:
        self.session.add(EmailSendAttempt(email_send_queue_id=item.id, provider_type=EmailProviderType.NULL_DRY_RUN, provider_status=ProviderStatus.DRY_RUN, attempt_status=SendAttemptStatus.DRY_RUN_PLANNED, attempt_number=item.retry_count + 1))
        item.queue_status = EmailSendQueueStatus.SEND_DRY_RUN_PLANNED
        self.session.flush()

    def _block_all(self, items, run, decision, status, reason: str) -> None:
        for item in items:
            self._block(item, run, decision, status, reason)

    def _block(self, item: EmailSendQueue, run: SendQueueRun, decision: Phase10Decision, status: EmailSendQueueStatus, reason: str) -> None:
        item.queue_status = status
        item.hold_reason = reason[:280]
        run.blocked_count += 1
        self.session.add(Phase10CandidateDecision(candidate_business_id=item.candidate_business_id, send_queue_run_id=run.id, email_send_queue_id=item.id, decision=decision, blocked=True, reason=reason))
        self.session.add(EmailSendAttempt(email_send_queue_id=item.id, provider_type=EmailProviderType(self.settings.email_provider) if self.settings.email_provider in EmailProviderType._value2member_map_ else EmailProviderType.CPANEL_SMTP, provider_status=ProviderStatus.BLOCKED, attempt_status=SendAttemptStatus.BLOCKED_BEFORE_SEND, attempt_number=item.retry_count + 1, error_type="BLOCKED", error_message=reason))
        self.session.add(SendAuditEvent(email_send_queue_id=item.id, actor="system", action=SendAuditAction.SEND_ATTEMPT_BLOCKED, reason=reason))
        self.session.flush()
