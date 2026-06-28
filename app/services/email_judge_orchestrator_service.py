from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    EmailAiJudgeDecision,
    EmailDraftVariantStatus,
    EmailJudgeDecisionValue,
    EmailJudgeMode,
    EmailJudgeOperation,
    EmailJudgeRunStatus,
    GateSeverity,
    Phase8Decision,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.email_draft_claim_usage import EmailDraftClaimUsage
from app.db.models.email_draft_evidence_link import EmailDraftEvidenceLink
from app.db.models.email_draft_precheck_result import EmailDraftPrecheckResult
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_judge_decision import EmailJudgeDecision
from app.db.models.email_judge_finding import EmailJudgeFinding
from app.db.models.email_judge_run import EmailJudgeRun
from app.db.models.email_variant_selection import EmailVariantSelection
from app.db.models.phase8_candidate_decision import Phase8CandidateDecision
from app.services.email_ai_judge_service import EmailAiJudgeService
from app.services.email_relevance_agent_service import EmailRelevanceAgentService
from app.services.email_rule_judge_service import EmailRuleJudgeService
from app.services.judge_disagreement_service import JudgeDisagreementService
from app.services.phase8_manual_review_service import Phase8ManualReviewService
from app.services.rejection_taxonomy_service import RejectionTaxonomyService
from app.services.rewrite_brief_service import RewriteBriefService
from app.services.variant_selection_service import VariantSelectionService
from app.settings import Settings


class EmailJudgeOrchestratorService:
    def __init__(self, session: Session, settings: Settings, ai_client=None, relevance_agent=None):
        self.session = session
        self.settings = settings
        self.ai_client = ai_client
        self.relevance_agent = relevance_agent

    def eligible(self, campaign_slug: str, generation_run_id: str | None = None, limit: int | None = None) -> list[EmailDraftVariant]:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            return []
        query = select(EmailDraftVariant).where(EmailDraftVariant.status == EmailDraftVariantStatus.JUDGE_PENDING)
        if generation_run_id:
            from app.db.models.email_generation_run import EmailGenerationRun

            gen = self.session.scalar(select(EmailGenerationRun).where(EmailGenerationRun.run_id == generation_run_id))
            if gen:
                query = query.where(EmailDraftVariant.email_generation_run_id == gen.id)
        drafts = self.session.scalars(query.order_by(EmailDraftVariant.id)).all()
        return list(drafts[:limit]) if limit else list(drafts)

    def judge_emails(self, campaign_slug: str, generation_run_id: str | None, commit: bool, limit: int | None = None) -> EmailJudgeRun:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        drafts = self.eligible(campaign_slug, generation_run_id, limit or self.settings.email_judge_max_drafts_per_run)
        mode = EmailJudgeMode.RULE_PLUS_AI if self.settings.email_judge_mode == "RULE_PLUS_AI" else EmailJudgeMode.RULE_ONLY
        run = EmailJudgeRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation=EmailJudgeOperation.PHASE8_FULL_JUDGE,
            status=EmailJudgeRunStatus.STARTED,
            dry_run=not commit,
            judge_mode=mode,
            model_provider="openai" if mode == EmailJudgeMode.RULE_PLUS_AI else None,
            model_name=self.settings.openai_judge_model or None,
            model_config_json={
                "temperature": self.settings.openai_judge_temperature,
                "max_tokens": self.settings.openai_judge_max_tokens,
                "api_key": "PRESENT" if self.settings.openai_api_key else "MISSING",
            },
            input_draft_count=len(drafts),
            metadata_json={"ai_judge_call_attempted": False, "no_send": True},
        )
        self.session.add(run)
        self.session.flush()
        if not drafts:
            run.status = EmailJudgeRunStatus.BLOCKED_BY_NO_ELIGIBLE_DRAFTS
        elif not commit:
            for draft in drafts:
                self._judge_one(run, draft, persist=False)
            run.status = EmailJudgeRunStatus.DRY_RUN_ONLY
        else:
            for draft in drafts:
                self._judge_one(run, draft, persist=True)
            for selection in VariantSelectionService(self.session).select_for_run(run.id):
                self.session.add(selection)
            self.session.flush()
            self._candidate_decisions(run.id)
            self._finish(run)
        run.finished_at = datetime.now(UTC)
        self.session.commit()
        return run

    def _judge_one(self, run: EmailJudgeRun, draft: EmailDraftVariant, persist: bool) -> None:
        evidence = self.session.scalars(select(EmailDraftEvidenceLink).where(EmailDraftEvidenceLink.email_draft_variant_id == draft.id)).all()
        claims = self.session.scalars(select(EmailDraftClaimUsage).where(EmailDraftClaimUsage.email_draft_variant_id == draft.id)).all()
        precheck = self.session.scalar(select(EmailDraftPrecheckResult).where(EmailDraftPrecheckResult.email_draft_variant_id == draft.id))
        rule_result, findings = EmailRuleJudgeService().judge(run.id, draft, list(evidence), list(claims), precheck, self.settings)
        ai_result = None
        ai_service = EmailAiJudgeService(self.settings, self.ai_client)
        ai_allowed, _ = ai_service.can_run(dry_run=run.dry_run)
        if ai_allowed:
            run.metadata_json = {**(run.metadata_json or {}), "ai_judge_call_attempted": True}
            ai_result = ai_service.judge(run.id, draft)
        decision, quality = self._decision(rule_result.passed, findings, ai_result)
        if self.settings.email_relevance_agent_enabled:
            candidate = self.session.get(CandidateBusiness, draft.candidate_business_id)
            agent = self.relevance_agent or EmailRelevanceAgentService(self.settings)
            relevance = agent.check(
                candidate.display_name if candidate else "",
                candidate.city if candidate else None,
                candidate.canonical_category if candidate else None,
                draft.subject_text,
                draft.body_text,
            )
            if (
                not relevance["relevant"]
                or relevance["score"] < self.settings.email_relevance_min_score
            ):
                decision = EmailJudgeDecisionValue.MANUAL_REVIEW_REQUIRED
                quality = min(quality, float(relevance["score"]))
                findings = [
                    *findings,
                    {
                        "finding_type": "BUSINESS_RELEVANCE_LOW",
                        "severity": GateSeverity.BLOCKER.value,
                        "message": f"Email may not match this business: {relevance['reason']}",
                        "evidence_json": relevance,
                    },
                ]
        if persist:
            self.session.add(rule_result)
            if ai_result:
                self.session.add(ai_result)
            for finding in findings:
                self.session.add(
                    EmailJudgeFinding(
                        email_judge_run_id=run.id,
                        email_draft_variant_id=draft.id,
                        finding_type=finding["finding_type"],
                        severity=finding["severity"],
                        message=finding["message"],
                        evidence_json=finding.get("evidence_json"),
                    )
                )
            self.session.add(
                EmailJudgeDecision(
                    email_judge_run_id=run.id,
                    candidate_business_id=draft.candidate_business_id,
                    email_draft_variant_id=draft.id,
                    decision=decision,
                    quality_score=quality,
                    ready_for_phase9=decision
                    in {
                        EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW,
                        EmailJudgeDecisionValue.APPROVED_WITH_WARNINGS_FOR_HUMAN_REVIEW,
                    },
                    manual_review_required=decision == EmailJudgeDecisionValue.MANUAL_REVIEW_REQUIRED,
                    rewrite_required=decision == EmailJudgeDecisionValue.REWRITE_REQUIRED,
                    blocked_reason=decision.value if "BLOCKED" in decision.value else None,
                    warnings_json=[f["message"] for f in findings if f["severity"] == GateSeverity.WARNING.value],
                )
            )
            if decision in {EmailJudgeDecisionValue.REWRITE_REQUIRED, EmailJudgeDecisionValue.MANUAL_REVIEW_REQUIRED} or "BLOCKED" in decision.value:
                self.session.add(RewriteBriefService().build(run.id, draft.id, draft.candidate_business_id, findings))
                self.session.add(Phase8ManualReviewService().item(draft.candidate_business_id, run.id, draft.id, decision.value))
            disagreement = JudgeDisagreementService().resolve(run.id, draft.id, rule_result.passed, ai_result.decision if ai_result else None)
            if disagreement:
                self.session.add(disagreement)
            # Advance the draft off JUDGE_PENDING so the next cycle judges NEW drafts. A TEXT-only
            # rejection is routed into the bounded rewrite loop (no lead burned for wording); a
            # CONTACT rejection or an exhausted lineage is NOT rewritten (rewording can't fix a
            # wrong recipient). Everything else is terminally JUDGED.
            rejected = decision in {
                EmailJudgeDecisionValue.REWRITE_REQUIRED,
                EmailJudgeDecisionValue.MANUAL_REVIEW_REQUIRED,
            } or "BLOCKED" in decision.value
            if (
                rejected
                and self.settings.email_rewrite_enabled
                and draft.rewrite_attempt < self.settings.email_rewrite_max_attempts
                and RejectionTaxonomyService().classify_judge(findings) == "TEXT_FIXABLE"
            ):
                draft.status = EmailDraftVariantStatus.AWAITING_REWRITE
            elif (
                rejected
                and self.settings.email_rewrite_enabled
                and draft.rewrite_attempt >= self.settings.email_rewrite_max_attempts
            ):
                draft.status = EmailDraftVariantStatus.REWRITE_EXHAUSTED
            else:
                draft.status = EmailDraftVariantStatus.JUDGED

    def _decision(self, rule_passed: bool, findings: list[dict[str, object]], ai_result) -> tuple[EmailJudgeDecisionValue, float]:
        blockers = [f for f in findings if f["severity"] == GateSeverity.BLOCKER.value]
        warnings = [f for f in findings if f["severity"] == GateSeverity.WARNING.value]
        quality = 85.0 if rule_passed else 40.0
        if ai_result:
            quality = min(quality, ai_result.overall_quality_score)
        if blockers:
            if any(f["finding_type"] == "EVIDENCE_MAPPING_MISSING" for f in blockers):
                return EmailJudgeDecisionValue.BLOCKED_EVIDENCE_MISSING, quality
            if any(f["finding_type"] in {"TOO_PROMOTIONAL", "SPAM_RISK"} for f in blockers):
                return EmailJudgeDecisionValue.BLOCKED_SPAM_RISK, quality
            return EmailJudgeDecisionValue.BLOCKED_COMPLIANCE_RISK, quality
        if ai_result and ai_result.decision == EmailAiJudgeDecision.REWRITE_REQUIRED:
            return EmailJudgeDecisionValue.REWRITE_REQUIRED, quality
        if ai_result and ai_result.decision == EmailAiJudgeDecision.BLOCK:
            return EmailJudgeDecisionValue.MANUAL_REVIEW_REQUIRED, quality
        if warnings or (ai_result and ai_result.decision == EmailAiJudgeDecision.PASS_WITH_WARNINGS):
            return EmailJudgeDecisionValue.APPROVED_WITH_WARNINGS_FOR_HUMAN_REVIEW, quality
        return EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW, quality

    def _candidate_decisions(self, run_id: int) -> None:
        selections = self.session.scalars(select(EmailVariantSelection).where(EmailVariantSelection.email_judge_run_id == run_id)).all()
        for selection in selections:
            ready = selection.preferred_email_draft_variant_id is not None
            self.session.add(
                Phase8CandidateDecision(
                    candidate_business_id=selection.candidate_business_id,
                    email_judge_run_id=run_id,
                    decision=Phase8Decision.APPROVED_FOR_HUMAN_REVIEW if ready else Phase8Decision.BLOCKED,
                    preferred_email_draft_variant_id=selection.preferred_email_draft_variant_id,
                    ready_for_phase9=ready,
                    blocked=not ready,
                    reason=selection.selection_reason,
                )
            )

    def _finish(self, run: EmailJudgeRun) -> None:
        decisions = self.session.scalars(select(EmailJudgeDecision).where(EmailJudgeDecision.email_judge_run_id == run.id)).all()
        run.approved_count = sum(1 for d in decisions if d.decision == EmailJudgeDecisionValue.APPROVED_FOR_HUMAN_REVIEW)
        run.approved_with_warnings_count = sum(1 for d in decisions if d.decision == EmailJudgeDecisionValue.APPROVED_WITH_WARNINGS_FOR_HUMAN_REVIEW)
        run.rewrite_required_count = sum(1 for d in decisions if d.rewrite_required)
        run.manual_review_count = sum(1 for d in decisions if d.manual_review_required)
        run.blocked_count = sum(1 for d in decisions if "BLOCKED" in d.decision.value)
        run.status = EmailJudgeRunStatus.COMPLETED_WITH_WARNINGS if run.blocked_count or run.rewrite_required_count or run.manual_review_count else EmailJudgeRunStatus.COMPLETED
