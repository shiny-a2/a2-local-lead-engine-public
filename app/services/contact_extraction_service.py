import re
from urllib.parse import urlparse

from app.core.enums import ContactSourceType, ContactType
from app.services.contact_risk_service import ContactRiskService

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}")


class ContactExtractionService:
    def extract_from_text(self, text: str, source_url: str | None = None, official_domain: str | None = None) -> list[dict]:
        contacts = []
        risk_service = ContactRiskService()
        for email in sorted(set(EMAIL_RE.findall(text or ""))):
            email_type, risk, blocked = risk_service.classify_email(email, official_domain)
            contacts.append(
                {
                    "contact_type": ContactType.EMAIL,
                    "contact_value": email,
                    "contact_domain": email.split("@")[-1].lower(),
                    "contact_source_url": source_url,
                    "contact_source_type": ContactSourceType.OFFICIAL_WEBSITE if source_url else ContactSourceType.SEARCH_RESULT,
                    "confidence": 0.8,
                    "risk_level": risk,
                    "allowed_for_outreach": risk_service.outreach_allowed(email_type, risk),
                    "requires_manual_review": risk.value != "LOW",
                    "blocked_reason": blocked,
                    "evidence_json": {"email_type": email_type.value},
                }
            )
        if "contact" in (text or "").lower() or (source_url and "contact" in source_url.lower()):
            contacts.append(
                {
                    "contact_type": ContactType.CONTACT_FORM,
                    "contact_value": source_url or "contact_form_detected",
                    "contact_domain": urlparse(source_url).netloc if source_url else None,
                    "contact_source_url": source_url,
                    "contact_source_type": ContactSourceType.OFFICIAL_WEBSITE,
                    "confidence": 0.5,
                    "risk_level": "MEDIUM",
                    "allowed_for_outreach": False,
                    "requires_manual_review": True,
                    "blocked_reason": "CONTACT_FORM_NOT_SUBMITTED_PHASE4",
                    "evidence_json": {"submitted": False},
                }
            )
        return contacts

