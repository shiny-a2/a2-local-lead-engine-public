import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    EmailDraftVariantStatus,
    EmailGenerationOperation,
    EmailGenerationRunStatus,
    Phase4WebsiteStatus,
    Phase6Decision,
    Phase7Decision,
)
from app.core.run_context import RunContext
from app.db.models.campaign import Campaign
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_contact_verification import CandidateContactVerification
from app.db.models.candidate_web_presence_verification import CandidateWebPresenceVerification
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_generation_input import EmailGenerationInput
from app.db.models.email_generation_run import EmailGenerationRun
from app.db.models.email_subject_candidate import EmailSubjectCandidate
from app.db.models.phase6_candidate_decision import Phase6CandidateDecision
from app.db.models.phase7_candidate_decision import Phase7CandidateDecision
from app.services.claim_usage_service import ClaimUsageService
from app.services.draft_precheck_service import DraftPrecheckService
from app.services.draft_similarity_service import DraftSimilarityService
from app.services.draft_variant_service import DraftVariantService
from app.services.email_generation_budget_service import EmailGenerationBudgetService
from app.services.email_input_assembler_service import EmailInputAssemblerService
from app.services.evidence_mapping_service import EvidenceMappingService
from app.services.prompt_template_service import PromptTemplateService
from app.services.subject_line_service import SubjectLineService
from app.settings import Settings

ModelClient = Callable[[dict[str, object]], str]


class EmailWriterService:
    def __init__(self, session: Session, settings: Settings, model_client: ModelClient | None = None):
        self.session = session
        self.settings = settings
        self.model_client = model_client

    def eligible(self, campaign_slug: str, limit: int | None = None) -> list[tuple[CandidateBusiness, Phase6CandidateDecision]]:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            return []
        decisions = self.session.scalars(
            select(Phase6CandidateDecision).where(
                Phase6CandidateDecision.ready_for_phase7.is_(True),
                Phase6CandidateDecision.decision.in_(
                    [
                        Phase6Decision.READY_FOR_PHASE_7_EMAIL_WRITER,
                        Phase6Decision.READY_FOR_PHASE_7_WITH_WARNINGS,
                    ]
                ),
            )
        ).all()
        rows = []
        for decision in decisions:
            candidate = self.session.get(CandidateBusiness, decision.candidate_business_id)
            if candidate and candidate.campaign_id == campaign.id:
                rows.append((candidate, decision))
        return rows[:limit] if limit else rows

    def generate(self, campaign_slug: str, batch_name: str | None, limit: int, commit: bool) -> EmailGenerationRun:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        template_service = PromptTemplateService(self.session)
        template_service.seed_defaults()
        candidates = self.eligible(campaign_slug, limit)
        variants = len(DraftVariantService().labels(self.settings))
        budget_ok, budget_reason = EmailGenerationBudgetService(self.settings).check(len(candidates), variants)
        run = EmailGenerationRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation=EmailGenerationOperation.PHASE7_FULL_GENERATION,
            status=EmailGenerationRunStatus.STARTED,
            dry_run=not commit,
            model_provider="openai" if commit else None,
            model_name=self.settings.openai_email_model or None,
            model_config_json={
                "temperature": self.settings.openai_email_temperature,
                "max_tokens": self.settings.openai_email_max_tokens,
                "api_key": "PRESENT" if self.settings.openai_api_key else "MISSING",
            },
            input_candidate_count=len(candidates),
            metadata_json={
                "batch_name": batch_name,
                "openai_calls_attempted": False,
                "token_estimate": EmailGenerationBudgetService(self.settings).estimate_tokens(len(candidates), variants),
            },
        )
        self.session.add(run)
        self.session.flush()
        if not budget_ok:
            run.status = EmailGenerationRunStatus.BLOCKED_BY_BUDGET
            run.metadata_json = {**(run.metadata_json or {}), "blocked_reason": budget_reason}
        elif not commit:
            run.status = EmailGenerationRunStatus.DRY_RUN_ONLY
        elif not self._generation_allowed():
            run.status = EmailGenerationRunStatus.BLOCKED_BY_AI_CONFIG
            for candidate, _ in candidates:
                self.session.add(
                    Phase7CandidateDecision(
                        candidate_business_id=candidate.id,
                        email_generation_run_id=run.id,
                        decision=Phase7Decision.BLOCKED_BY_AI_CONFIG,
                        ready_for_phase8=False,
                        reject_reason="AI/email drafting flags or OpenAI key missing, and local writer disabled.",
                    )
                )
        else:
            ai = self._ai_allowed()
            if not ai:
                # Free keyless path: deterministic local template writer (no OpenAI call).
                run.model_provider = "local_template"
                run.model_name = "local_template_v1"
            run.metadata_json = {
                **(run.metadata_json or {}),
                "openai_calls_attempted": ai,
                "writer_mode": "openai" if ai else "local_template",
            }
            for candidate, phase6 in candidates:
                self._generate_for_candidate(run, candidate, phase6)
        self.session.flush()
        self._finish(run)
        self.session.commit()
        return run

    def _ai_allowed(self) -> bool:
        return (
            self.settings.ai_generation_enabled
            and self.settings.email_drafting_enabled
            and bool(self.settings.openai_api_key)
        )

    def _generation_allowed(self) -> bool:
        # Either a real AI path (OpenAI) is configured, or the free local writer is enabled.
        return self._ai_allowed() or (
            self.settings.email_drafting_enabled and self.settings.email_local_writer_enabled
        )

    def _generate_for_candidate(
        self,
        run: EmailGenerationRun,
        candidate: CandidateBusiness,
        phase6: Phase6CandidateDecision,
    ) -> None:
        generation_input = EmailInputAssemblerService(self.session, self.settings).assemble(run.id, candidate, phase6)
        self.session.add(generation_input)
        self.session.flush()
        template = PromptTemplateService(self.session).choose(generation_input.input_snapshot_json.get("campaign_lane", "NO_WEBSITE"), candidate.canonical_category)
        self.session.add(PromptTemplateService(self.session).snapshot(run.id, template, run.model_config_json or {}))
        try:
            output = self._call_model(generation_input)
            payload = json.loads(output)
            drafts = payload["drafts"]
        except Exception:
            run.failed_count += 1
            self.session.add(
                Phase7CandidateDecision(
                    candidate_business_id=candidate.id,
                    email_generation_run_id=run.id,
                    decision=Phase7Decision.FAILED_GENERATION,
                    reject_reason="invalid JSON output",
                )
            )
            return
        for item in drafts[: self.settings.email_generation_max_variants_per_candidate]:
            self._store_variant(run, candidate, generation_input, template.tone_profile, item)

    def _call_model(self, generation_input: EmailGenerationInput) -> str:
        if self.model_client:
            return self.model_client(generation_input.input_snapshot_json)
        if self._ai_allowed():
            return self._openai_json(generation_input)
        return self._local_json(generation_input)

    def _openai_json(self, generation_input: EmailGenerationInput) -> str:
        from app.services.openai_client import OpenAIClient

        snapshot = generation_input.input_snapshot_json or {}
        offers = [o.get("text") for o in (generation_input.offer_blocks_json or []) if o.get("text")]
        if not offers and snapshot.get("offer_summary"):
            offers = [snapshot["offer_summary"]]
        placeholder = snapshot.get("unsubscribe_placeholder", self.settings.email_unsubscribe_placeholder)
        system = (
            "You write short, honest, non-promotional cold outreach emails for Amirali "
            "Yaghouti, who builds simple websites for local businesses. LENGTH IS CRITICAL: the "
            "body MUST be 5 to 6 complete sentences and AT LEAST "
            f"{self.settings.email_min_words + 30} words (emails under "
            f"{self.settings.email_min_words + 10} words are auto-rejected, so never write a "
            "3-4 sentence email). Reach the length naturally with: one sentence naming the "
            "business and its area, one or two on how a simple website helps customers act, one "
            "that it can start small and grow, one introducing Amirali, and one short closing "
            f"question. Keep it under {self.settings.email_max_words - 10} words. Use a calm, plain "
            "tone with NO exclamation marks. Use exactly one "
            "soft call to action (a question, no hard sell); ground every claim ONLY in the "
            "offer ideas/allowed claims; never invent facts, prices, guarantees, commissions, or "
            "mention Google Maps; sign as Amirali Yaghouti; end the body with the literal token "
            f"{placeholder}. Return ONLY JSON: {{\"drafts\":[{{\"variant_label\":\"A\",\"subject\""
            ":\"...\",\"body\":\"...\",\"evidence_keys\":[\"business_name\",\"local_context\"],"
            "\"claim_texts\":[\"...\"]}, {\"variant_label\":\"B\",...}]}. Provide exactly two "
            "variants A and B with subjects of at most "
            f"{self.settings.email_max_subject_words} words."
        )
        user = json.dumps(
            {
                "business_name": snapshot.get("business_name"),
                "local_context": snapshot.get("local_context"),
                "category": snapshot.get("category"),
                "campaign_lane": snapshot.get("campaign_lane"),
                "offer_ideas": offers,
                "allowed_claims": generation_input.allowed_claims_json or offers,
                "do_not_say": generation_input.blocked_claims_json or [],
            },
            ensure_ascii=False,
        )
        return OpenAIClient(self.settings).chat_json(system, user)

    def _local_json(self, generation_input: EmailGenerationInput) -> str:
        name = generation_input.input_snapshot_json["business_name"]
        local = generation_input.input_snapshot_json["local_context"]
        offer = generation_input.offer_blocks_json[0]["text"] if generation_input.offer_blocks_json else "a simpler customer action path"
        body = (
            f"I was looking at {name} around {local} and noticed the public web presence could point customers a little more directly. "
            f"One small idea is {offer}. "
            "It could start as a lightweight page with the useful details in one place, then grow only if it proves useful. "
            "I am Amirali Yaghouti, and I build simple local-business web systems. "
            f"Would a quick idea for a simple first version be useful? {self.settings.email_unsubscribe_placeholder}"
        )
        return json.dumps(
            {
                "drafts": [
                    {"variant_label": "A", "subject": "A simple website idea", "body": body, "evidence_keys": ["business_name", "local_context"], "claim_texts": [offer]},
                    {"variant_label": "B", "subject": f"Quick idea for {name}".split(",")[0], "body": body.replace("One small idea", "A softer first step"), "evidence_keys": ["business_name", "local_context"], "claim_texts": [offer]},
                ]
            }
        )

    def _store_variant(self, run, candidate, generation_input, tone_profile, item) -> None:
        subject = str(item.get("subject", "A simple website idea"))
        body = str(item.get("body", ""))
        subject_meta = SubjectLineService().generate(candidate.display_name, str(item.get("variant_label", "A")), self.settings)
        subject = subject if subject_meta["allowed_for_judge"] else str(subject_meta["subject_text"])
        draft = EmailDraftVariant(
            candidate_business_id=candidate.id,
            email_generation_run_id=run.id,
            variant_label=str(item.get("variant_label", "A")),
            subject_text=subject,
            body_text=body,
            word_count=len(body.split()),
            tone_profile=tone_profile,
            campaign_lane=str(generation_input.input_snapshot_json.get("campaign_lane", "UNKNOWN")),
            category=candidate.canonical_category,
            status=EmailDraftVariantStatus.DRAFT_CREATED,
        )
        self.session.add(draft)
        self.session.flush()
        self.session.add(EmailSubjectCandidate(candidate_business_id=candidate.id, email_generation_run_id=run.id, variant_label=draft.variant_label, **subject_meta))
        for link in EvidenceMappingService().links(draft.id, generation_input):
            self.session.add(link)
        for usage in ClaimUsageService().usages(draft.id, body, generation_input):
            self.session.add(usage)
        similarity = DraftSimilarityService(self.session, self.settings).compare(draft)
        self.session.add(similarity)
        precheck = DraftPrecheckService().check(
            draft.id,
            subject,
            body,
            anchors=len(set(item.get("evidence_keys", []))) + min(1, len(item.get("claim_texts", []))),
            settings=self.settings,
            similarity_ok=similarity.decision.value != "BLOCKED_TOO_SIMILAR",
        )
        self.session.add(precheck)
        draft.status = (
            EmailDraftVariantStatus.JUDGE_PENDING
            if precheck.precheck_status.value == "PASSED"
            else EmailDraftVariantStatus.BLOCKED_PRECHECK
        )
        self.session.add(
            Phase7CandidateDecision(
                candidate_business_id=candidate.id,
                email_generation_run_id=run.id,
                decision=Phase7Decision.DRAFT_CREATED_JUDGE_PENDING
                if draft.status == EmailDraftVariantStatus.JUDGE_PENDING
                else Phase7Decision.NEEDS_MANUAL_REVIEW_BEFORE_JUDGE,
                ready_for_phase8=draft.status == EmailDraftVariantStatus.JUDGE_PENDING,
                manual_review_required=draft.status != EmailDraftVariantStatus.JUDGE_PENDING,
                warnings_json=precheck.risk_flags_json,
            )
        )

    # ---- Website IMPROVEMENT campaign (separate from the no-website "build" campaign) ----

    def generate_improvement(self, campaign_slug: str, limit: int, commit: bool) -> EmailGenerationRun:
        """Generate 'improve your existing website' emails for businesses that already
        have a real site and a safe contact. Separate batch from the no-website campaign."""
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            raise ValueError("campaign not found")
        candidates = self._improvement_eligible(campaign_slug, limit)
        run = EmailGenerationRun(
            run_id=RunContext().run_id,
            campaign_id=campaign.id,
            operation=EmailGenerationOperation.PHASE7_FULL_GENERATION,
            status=EmailGenerationRunStatus.STARTED,
            dry_run=not commit,
            model_provider="openai" if self._ai_allowed() else "local_template",
            model_name=self.settings.openai_email_model or "local_template_v1",
            input_candidate_count=len(candidates),
            metadata_json={
                "campaign_type": "improvement",
                "openai_calls_attempted": self._ai_allowed(),
            },
        )
        self.session.add(run)
        self.session.flush()
        if not candidates:
            run.status = EmailGenerationRunStatus.DRY_RUN_ONLY
        elif not commit:
            run.status = EmailGenerationRunStatus.DRY_RUN_ONLY
        elif not self._generation_allowed():
            run.status = EmailGenerationRunStatus.BLOCKED_BY_AI_CONFIG
        else:
            for candidate, website_url in candidates:
                self._generate_improvement_for_candidate(run, candidate, website_url)
        self.session.flush()
        self._finish(run)
        self.session.commit()
        return run

    def _improvement_eligible(self, campaign_slug: str, limit: int | None) -> list[tuple[CandidateBusiness, str]]:
        campaign = self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
        if campaign is None:
            return []
        rows: list[tuple[CandidateBusiness, str]] = []
        candidates = self.session.scalars(
            select(CandidateBusiness).where(CandidateBusiness.campaign_id == campaign.id)
        ).all()
        for candidate in candidates:
            web = self.session.scalar(
                select(CandidateWebPresenceVerification)
                .where(
                    CandidateWebPresenceVerification.candidate_business_id == candidate.id,
                    CandidateWebPresenceVerification.website_status
                    == Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL,
                )
                .order_by(CandidateWebPresenceVerification.id.desc())
            )
            if web is None:
                continue
            contact = self.session.scalar(
                select(CandidateContactVerification)
                .where(
                    CandidateContactVerification.candidate_business_id == candidate.id,
                    CandidateContactVerification.outreach_contact_allowed.is_(True),
                )
                .order_by(CandidateContactVerification.id.desc())
            )
            if contact is None:
                continue
            rows.append((candidate, web.official_website_url or web.official_website_domain or ""))
        return rows[:limit] if limit else rows

    def _generate_improvement_for_candidate(self, run, candidate, website_url) -> None:
        gen_input = self._improvement_input(run, candidate, website_url)
        self.session.add(gen_input)
        self.session.flush()
        try:
            payload = json.loads(self._improvement_model_output(gen_input, website_url))
            drafts = payload["drafts"]
        except Exception:
            run.failed_count += 1
            self.session.add(
                Phase7CandidateDecision(
                    candidate_business_id=candidate.id,
                    email_generation_run_id=run.id,
                    decision=Phase7Decision.FAILED_GENERATION,
                    reject_reason="invalid JSON output (improvement)",
                )
            )
            return
        for item in drafts[: self.settings.email_generation_max_variants_per_candidate]:
            self._store_variant(run, candidate, gen_input, "improvement", item)

    def _improvement_input(self, run, candidate, website_url) -> EmailGenerationInput:
        local = candidate.suburb or candidate.city or ""
        offer = "a clearer, faster, more modern version of your current website"
        snapshot = {
            "business_name": candidate.display_name,
            "category": candidate.canonical_category,
            "local_context": local,
            "campaign_lane": "IMPROVEMENT",
            "offer_summary": offer,
            "website_url": website_url,
            "unsubscribe_placeholder": self.settings.email_unsubscribe_placeholder,
        }
        payload = {"input_snapshot": snapshot, "offer": offer, "website": website_url}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return EmailGenerationInput(
            email_generation_run_id=run.id,
            candidate_business_id=candidate.id,
            phase6_decision_id=None,
            input_snapshot_json=snapshot,
            input_snapshot_hash=digest,
            allowed_claims_json=[offer],
            blocked_claims_json=[],
            offer_blocks_json=[],
            verified_evidence_json=[
                {"type": "business_name", "value": candidate.display_name},
                {"type": "local_context", "value": local},
            ],
            style_constraints_json={
                "min_words": self.settings.email_min_words,
                "max_words": self.settings.email_max_words,
                "no_send": True,
            },
            cta_options_json=["quick_idea", "improvement_idea"],
        )

    def _improvement_model_output(self, gen_input, website_url) -> str:
        if self._ai_allowed():
            return self._openai_improvement_json(gen_input, website_url)
        return self._local_improvement_json(gen_input, website_url)

    def _openai_improvement_json(self, gen_input, website_url) -> str:
        from app.services.openai_client import OpenAIClient

        snap = gen_input.input_snapshot_json
        placeholder = snap.get("unsubscribe_placeholder", self.settings.email_unsubscribe_placeholder)
        system = (
            "You write a short, honest improvement-pitch cold email for Amirali Yaghouti, who "
            "refreshes and improves websites for local businesses. IMPORTANT: this business "
            "ALREADY HAS a website; never say they lack one. Offer to make their existing site "
            "clearer, faster, more modern, and better at turning visitors into customers. Write "
            "the body as 5 to 6 complete sentences. The "
            f"body MUST be between {self.settings.email_min_words + 30} and "
            f"{self.settings.email_max_words - 10} words (never under "
            f"{self.settings.email_min_words + 10}); exactly one soft question as the call to "
            "action; use a calm, plain tone with NO exclamation marks; invent no facts (no fake "
            "problems, awards, prices); sign as Amirali "
            f"Yaghouti; end the body with the literal token {placeholder}. Return ONLY JSON: "
            '{"drafts":[{"variant_label":"A","subject":"...","body":"...","evidence_keys":'
            '["business_name","local_context"],"claim_texts":["..."]}, {"variant_label":"B",...}]}'
            f" with subjects of at most {self.settings.email_max_subject_words} words."
        )
        user = json.dumps(
            {
                "business_name": snap.get("business_name"),
                "local_context": snap.get("local_context"),
                "category": snap.get("category"),
                "current_website": website_url,
                "offer_idea": snap.get("offer_summary"),
            },
            ensure_ascii=False,
        )
        return OpenAIClient(self.settings).chat_json(system, user)

    def _local_improvement_json(self, gen_input, website_url) -> str:
        snap = gen_input.input_snapshot_json
        name = snap["business_name"]
        local = snap["local_context"]
        body = (
            f"I came across {name} around {local} and had a look at your current website. "
            "It already does the basics, and with a few focused changes it could load faster, "
            "read more clearly on phones, and guide visitors to contact or book you more "
            "directly. I am Amirali Yaghouti, and I refresh simple local-business websites so "
            "they convert a little better without a full rebuild. The work can start small and "
            "only grow if it proves useful to you. "
            f"Would a quick, no-pressure idea for your site be useful? {self.settings.email_unsubscribe_placeholder}"
        )
        return json.dumps(
            {
                "drafts": [
                    {"variant_label": "A", "subject": f"A quick idea for {name}".split(",")[0], "body": body, "evidence_keys": ["business_name", "local_context"], "claim_texts": [snap["offer_summary"]]},
                    {"variant_label": "B", "subject": "Freshening up your website", "body": body.replace("a few focused changes", "a light refresh"), "evidence_keys": ["business_name", "local_context"], "claim_texts": [snap["offer_summary"]]},
                ]
            }
        )

    def _finish(self, run: EmailGenerationRun) -> None:
        variants = self.session.scalars(select(EmailDraftVariant).where(EmailDraftVariant.email_generation_run_id == run.id)).all()
        run.draft_created_count = len(variants)
        run.blocked_count = sum(1 for row in variants if row.status == EmailDraftVariantStatus.BLOCKED_PRECHECK)
        run.manual_review_count = run.blocked_count
        if run.status == EmailGenerationRunStatus.STARTED:
            run.status = EmailGenerationRunStatus.COMPLETED_WITH_WARNINGS if run.manual_review_count else EmailGenerationRunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
