import re

from app.core.enums import ContactRiskLevel, EmailType

# Role/inbox mailbox prefixes that belong to the BUSINESS, not a person. An all-letter local
# part that is NOT one of these used to be mislabelled "personal-looking" and blocked, which
# starved the funnel (enquiries@/appointments@/office@/service@/salon@ are legitimate business
# inboxes). The recipient still must pass the domain-match check below and the fail-closed GPT
# pre-send QA gate before any real send.
ROLE_PREFIXES = {
    "info", "hello", "hi", "contact", "contactus", "enquiries", "enquiry", "enquire",
    "inquiries", "inquiry", "admin", "office", "officemanager", "reception", "bookings",
    "booking", "book", "appointment", "appointments", "orders", "order", "sales", "accounts",
    "support", "service", "services", "customerservice", "team", "mail", "email", "reservations",
    "reserve", "help", "care", "careers", "marketing", "franchising", "salon", "studio", "clinic",
    "shop", "store", "frontdesk", "desk", "general", "manager", "owner",
}
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
        # "first.last" is a genuine personal name only when NEITHER token is a role word.
        name = re.match(r"^([a-z]+)\.([a-z]+)$", local)
        if name and name.group(1) not in ROLE_PREFIXES and name.group(2) not in ROLE_PREFIXES:
            return EmailType.PERSONAL, ContactRiskLevel.HIGH, "PERSONAL_LOOKING_EMAIL"
        # A single all-letter local that is NOT a known role inbox looks like a person's name —
        # keep it blocked (the pre-send GPT QA gate is the final arbiter on anything subtler).
        if re.match(r"^[a-z]{3,}$", local):
            return EmailType.PERSONAL, ContactRiskLevel.HIGH, "PERSONAL_LOOKING_EMAIL"
        return EmailType.GENERIC_BUSINESS, ContactRiskLevel.LOW, None

    def outreach_allowed(self, email_type: EmailType, risk: ContactRiskLevel) -> bool:
        return email_type in {EmailType.GENERIC_BUSINESS, EmailType.ROLE_BASED} and risk == ContactRiskLevel.LOW

