from app.core.enums import EmailJudgeFindingType, GateSeverity
from app.db.models.email_draft_claim_usage import EmailDraftClaimUsage
from app.db.models.email_draft_evidence_link import EmailDraftEvidenceLink
from app.db.models.email_draft_precheck_result import EmailDraftPrecheckResult
from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.email_rule_judge_result import EmailRuleJudgeResult
from app.settings import Settings


class EmailRuleJudgeService:
    blockers = {
        EmailJudgeFindingType.ABSOLUTE_NO_WEBSITE_CLAIM: ["you don't have a website", "you do not have a website"],
        EmailJudgeFindingType.COMMISSION_CLAIM: ["stop paying commissions", "commission elimination"],
        EmailJudgeFindingType.GUARANTEED_RESULT_CLAIM: ["guaranteed", "guarantee bookings", "save thousands"],
        EmailJudgeFindingType.GOOGLE_MAPS_REFERENCE: ["google maps"],
        EmailJudgeFindingType.PLATFORM_ATTACK: ["directories are bad", "social media is bad", "replace all platforms"],
        EmailJudgeFindingType.CREEPY_EVIDENCE: ["owner name", "nzbn", "raw phone", "personal email"],
        EmailJudgeFindingType.PRICE_CLAIM_RISK: ["$99", "final price", "fixed quote"],
    }
    spam_terms = ["limited time", "free money", "act now", "best price"]

    def judge(
        self,
        run_id: int,
        draft: EmailDraftVariant,
        evidence_links: list[EmailDraftEvidenceLink],
        claim_usages: list[EmailDraftClaimUsage],
        precheck: EmailDraftPrecheckResult | None,
        settings: Settings,
    ) -> tuple[EmailRuleJudgeResult, list[dict[str, object]]]:
        text = f"{draft.subject_text}\n{draft.body_text}".lower()
        findings: list[dict[str, object]] = []
        for finding_type, terms in self.blockers.items():
            for term in terms:
                if term in text:
                    findings.append(self._finding(finding_type, GateSeverity.BLOCKER, f"Blocked phrase: {term}"))
                    break
        if settings.email_unsubscribe_placeholder not in draft.body_text:
            findings.append(self._finding(EmailJudgeFindingType.MISSING_UNSUBSCRIBE, GateSeverity.BLOCKER, "Missing unsubscribe placeholder."))
        if "amirali" not in text:
            findings.append(self._finding(EmailJudgeFindingType.MISSING_SENDER_IDENTITY, GateSeverity.BLOCKER, "Missing sender identity."))
        if draft.body_text.count("?") > 1:
            findings.append(self._finding(EmailJudgeFindingType.MULTIPLE_CTA, GateSeverity.BLOCKER, "Multiple CTAs detected."))
        if len(draft.subject_text.split()) > settings.email_max_subject_words:
            findings.append(self._finding(EmailJudgeFindingType.SPAM_RISK, GateSeverity.WARNING, "Subject is too long."))
        if any(term in text for term in self.spam_terms):
            findings.append(self._finding(EmailJudgeFindingType.SPAM_RISK, GateSeverity.BLOCKER, "Spam-like wording detected."))
        if not evidence_links:
            findings.append(self._finding(EmailJudgeFindingType.EVIDENCE_MAPPING_MISSING, GateSeverity.BLOCKER, "Missing evidence mapping."))
        if not claim_usages:
            findings.append(self._finding(EmailJudgeFindingType.UNSUPPORTED_CLAIM, GateSeverity.WARNING, "No allowed claim usage recorded."))
        if precheck and precheck.precheck_status.value == "FAILED":
            findings.append(self._finding(EmailJudgeFindingType.TONE_RISK, GateSeverity.BLOCKER, "Phase 7 precheck failed."))
        blocker_count = sum(1 for finding in findings if finding["severity"] == GateSeverity.BLOCKER.value)
        warning_count = sum(1 for finding in findings if finding["severity"] == GateSeverity.WARNING.value)
        result = EmailRuleJudgeResult(
            email_judge_run_id=run_id,
            email_draft_variant_id=draft.id,
            passed=blocker_count == 0,
            blocker_count=blocker_count,
            warning_count=warning_count,
            truthfulness_passed=not any(f["finding_type"] == EmailJudgeFindingType.UNSUPPORTED_CLAIM.value and f["severity"] == GateSeverity.BLOCKER.value for f in findings),
            evidence_alignment_passed=bool(evidence_links),
            blocked_claims_passed=not any(not usage.allowed for usage in claim_usages),
            unsubscribe_passed=settings.email_unsubscribe_placeholder in draft.body_text,
            sender_identity_passed="amirali" in text,
            cta_passed=draft.body_text.count("?") <= 1,
            creepy_evidence_passed=not any(f["finding_type"] == EmailJudgeFindingType.CREEPY_EVIDENCE.value for f in findings),
            economic_claims_passed=not any(f["finding_type"] in {EmailJudgeFindingType.COMMISSION_CLAIM.value, EmailJudgeFindingType.GUARANTEED_RESULT_CLAIM.value} for f in findings),
            findings_json=findings,
        )
        return result, findings

    def _finding(self, finding_type: EmailJudgeFindingType, severity: GateSeverity, message: str) -> dict[str, object]:
        return {"finding_type": finding_type.value, "severity": severity.value, "message": message}
