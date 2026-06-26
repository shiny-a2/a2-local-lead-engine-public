from app.core.enums import DraftPrecheckStatus
from app.db.models.email_draft_precheck_result import EmailDraftPrecheckResult
from app.settings import Settings


class DraftPrecheckService:
    blocked_terms = [
        "you don't have a website",
        "google maps",
        "guaranteed",
        "stop paying commissions",
        "save thousands",
        "limited time",
        "losing customers",
    ]

    def check(
        self,
        draft_id: int,
        subject: str,
        body: str,
        anchors: int,
        settings: Settings,
        *,
        similarity_ok: bool = True,
        prompt_injection_ok: bool = True,
    ) -> EmailDraftPrecheckResult:
        word_count = len(body.split())
        subject_ok = len(subject.split()) <= settings.email_max_subject_words
        blocked_words_ok = not any(term in body.lower() or term in subject.lower() for term in self.blocked_terms)
        unsubscribe_ok = (
            settings.email_unsubscribe_placeholder in body
            if settings.email_include_unsubscribe_placeholder
            else True
        )
        checks = {
            "word_count_ok": settings.email_min_words <= word_count <= settings.email_max_words,
            "subject_ok": subject_ok,
            "personalization_ok": anchors >= settings.email_min_personalization_anchors,
            "blocked_words_ok": blocked_words_ok,
            "claim_permission_ok": blocked_words_ok,
            "economic_claim_ok": blocked_words_ok,
            "tone_ok": "!" not in body,
            "cta_ok": body.lower().count("?") <= 1,
            "unsubscribe_placeholder_ok": unsubscribe_ok,
            "similarity_ok": similarity_ok,
            "prompt_injection_ok": prompt_injection_ok,
        }
        flags = [key for key, ok in checks.items() if not ok]
        status = DraftPrecheckStatus.PASSED if not flags else DraftPrecheckStatus.FAILED
        return EmailDraftPrecheckResult(
            email_draft_variant_id=draft_id,
            precheck_status=status,
            risk_flags_json=flags,
            **checks,
        )
