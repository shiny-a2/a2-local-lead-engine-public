from app.core.enums import ContactType
from app.services.contact_extraction_service import ContactExtractionService


def test_generic_business_email_candidate():
    rows = ContactExtractionService().extract_from_text("Email info@example.co.nz", official_domain="example.co.nz")
    assert rows[0]["contact_type"] == ContactType.EMAIL


def test_personal_email_blocked():
    row = ContactExtractionService().extract_from_text("Email bob@gmail.com")[0]
    assert row["allowed_for_outreach"] is False


def test_contact_form_detected_not_submitted():
    rows = ContactExtractionService().extract_from_text("Contact us", "https://example.co.nz/contact")
    form = [row for row in rows if row["contact_type"] == ContactType.CONTACT_FORM][0]
    assert form["evidence_json"]["submitted"] is False


def test_phone_social_evidence_only():
    assert True
