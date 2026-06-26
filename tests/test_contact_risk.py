from app.core.enums import ContactRiskLevel, EmailType
from app.services.contact_risk_service import ContactRiskService


def test_info_hello_contact_allowed_low_risk():
    email_type, risk, _ = ContactRiskService().classify_email("info@example.co.nz", "example.co.nz")
    assert email_type == EmailType.ROLE_BASED
    assert risk == ContactRiskLevel.LOW


def test_firstname_personal_looking_blocked():
    _, risk, blocked = ContactRiskService().classify_email("amirali@example.co.nz", "example.co.nz")
    assert risk == ContactRiskLevel.HIGH
    assert blocked == "PERSONAL_LOOKING_EMAIL"


def test_gmail_personal_domain_blocked():
    email_type, risk, _ = ContactRiskService().classify_email("hello@gmail.com")
    assert email_type == EmailType.PERSONAL
    assert risk == ContactRiskLevel.BLOCKED


def test_unrelated_domain_blocked():
    _, risk, blocked = ContactRiskService().classify_email("info@other.co.nz", "example.co.nz")
    assert risk == ContactRiskLevel.HIGH
    assert blocked == "CONTACT_DOMAIN_MISMATCH"

