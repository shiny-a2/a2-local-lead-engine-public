import re

from app.core.enums import ContactRiskLevel, EmailType

ROLE_PREFIXES = {"info", "hello", "contact", "admin", "bookings", "support", "team"}
PERSONAL_DOMAINS = {"gmail.com", "outlook.com", "hotmail.com", "yahoo.com"}


class ContactRiskService:
    def classify_email(self, email: str, official_domain: str | None = None) -> tuple[EmailType, ContactRiskLevel, str | None]:
        local, _, domain = email.lower().partition("@")
        if domain in PERSONAL_DOMAINS:
            return EmailType.PERSONAL, ContactRiskLevel.BLOCKED, "PERSONAL_EMAIL_DOMAIN"
        if official_domain and domain and official_domain not in domain:
            return EmailType.UNKNOWN, ContactRiskLevel.HIGH, "CONTACT_DOMAIN_MISMATCH"
        if local in ROLE_PREFIXES:
            return EmailType.ROLE_BASED, ContactRiskLevel.LOW, None
        if re.match(r"^[a-z]+\.[a-z]+$", local) or re.match(r"^[a-z]{3,}$", local):
            return EmailType.PERSONAL, ContactRiskLevel.HIGH, "PERSONAL_LOOKING_EMAIL"
        return EmailType.GENERIC_BUSINESS, ContactRiskLevel.LOW, None

    def outreach_allowed(self, email_type: EmailType, risk: ContactRiskLevel) -> bool:
        return email_type in {EmailType.GENERIC_BUSINESS, EmailType.ROLE_BASED} and risk == ContactRiskLevel.LOW

