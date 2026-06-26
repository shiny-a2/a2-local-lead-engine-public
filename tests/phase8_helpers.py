import json

from app.core.enums import DraftPrecheckStatus, EmailClaimRiskLevel, EmailDraftVariantStatus
from app.db.models.email_draft_claim_usage import EmailDraftClaimUsage
from app.db.models.email_draft_evidence_link import EmailDraftEvidenceLink
from app.db.models.email_draft_precheck_result import EmailDraftPrecheckResult
from app.db.models.email_draft_variant import EmailDraftVariant
from app.services.email_writer_service import EmailWriterService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate

SAFE_BODY = (
    "I was looking at Example Phase Six Studio around Ponsonby and noticed a simple owned page could make useful details easier to find. "
    "A lightweight services and booking idea could keep the customer action path in one calm place, without changing anything else. "
    "It can start small and only grow if it proves useful. "
    "I am Amirali Yaghouti, and I build simple local-business web systems. "
    "Would a quick idea for a simple first version be useful? {{unsubscribe_url}}"
)


def draft(
    body: str = SAFE_BODY,
    subject: str = "A simple website idea",
    draft_id: int = 1,
    status: EmailDraftVariantStatus = EmailDraftVariantStatus.JUDGE_PENDING,
) -> EmailDraftVariant:
    return EmailDraftVariant(
        id=draft_id,
        candidate_business_id=1,
        email_generation_run_id=1,
        variant_label="A",
        subject_text=subject,
        body_text=body,
        word_count=len(body.split()),
        tone_profile="plain_helpful",
        campaign_lane="NO_WEBSITE",
        category="barber",
        status=status,
    )


def evidence(draft_id: int = 1) -> list[EmailDraftEvidenceLink]:
    return [
        EmailDraftEvidenceLink(
            email_draft_variant_id=draft_id,
            evidence_type="business_name",
            evidence_source_table="verified_personalization_evidence",
            evidence_source_id=1,
            used_in_sentence="Example Phase Six Studio around Ponsonby",
            confidence=0.9,
        )
    ]


def allowed_claim(draft_id: int = 1) -> list[EmailDraftClaimUsage]:
    return [
        EmailDraftClaimUsage(
            email_draft_variant_id=draft_id,
            claim_type="can_say_could_not_find_dedicated_website",
            claim_text="simple owned page",
            claim_permission_id=1,
            allowed=True,
            risk_level=EmailClaimRiskLevel.LOW,
            reason="Conservative evidence-backed claim.",
        )
    ]


def passing_precheck(draft_id: int = 1) -> EmailDraftPrecheckResult:
    return EmailDraftPrecheckResult(
        email_draft_variant_id=draft_id,
        precheck_status=DraftPrecheckStatus.PASSED,
        word_count_ok=True,
        subject_ok=True,
        personalization_ok=True,
        blocked_words_ok=True,
        claim_permission_ok=True,
        economic_claim_ok=True,
        tone_ok=True,
        cta_ok=True,
        unsubscribe_placeholder_ok=True,
        similarity_ok=True,
        prompt_injection_ok=True,
        risk_flags_json=[],
    )


def make_judge_pending_draft(session):
    campaign, _ = make_phase7_ready_candidate(session)

    def client(_payload):
        return json.dumps(
            {
                "drafts": [
                    {
                        "variant_label": "A",
                        "subject": "A simple website idea",
                        "body": SAFE_BODY,
                        "evidence_keys": ["business_name", "local_context"],
                        "claim_texts": ["simple owned page"],
                    }
                ]
            }
        )

    settings = Settings(ai_generation_enabled=True, email_drafting_enabled=True, openai_api_key="sk-test")
    generation_run = EmailWriterService(session, settings, client).generate(campaign.slug, None, 10, commit=True)
    draft_row = session.query(EmailDraftVariant).filter_by(status=EmailDraftVariantStatus.JUDGE_PENDING).first()
    assert draft_row is not None
    return campaign, generation_run, draft_row
