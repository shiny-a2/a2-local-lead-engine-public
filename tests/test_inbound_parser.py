from app.db.models.inbound_attachment import InboundAttachment
from app.services.inbound_message_parser_service import InboundMessageParserService
from tests.phase11_helpers import import_message, inbox_settings


def test_parser_extracts_and_sanitizes_html():
    raw = b"From: a@example.com\r\nTo: b@example.com\r\nSubject: Hi\r\n\r\n<html><script>x</script>Hello</html>"
    parsed = InboundMessageParserService(inbox_settings()).parse_bytes(raw, "7")
    assert "Hello" in parsed.body_text_sanitized
    assert "<script" not in parsed.body_text_sanitized


def test_body_limit_enforced():
    parsed = InboundMessageParserService(inbox_settings(inbound_max_body_chars=5)).parse_bytes(
        b"From: a@example.com\r\nTo: b@example.com\r\nSubject: Hi\r\n\r\n123456789",
        "7",
    )
    assert parsed.body_text_sanitized == "12345"


def test_attachment_metadata_only(session):
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["From"] = "a@example.com"
    msg["To"] = "b@example.com"
    msg["Subject"] = "file"
    msg.set_content("see attached")
    msg.add_attachment(b"abc", maintype="text", subtype="plain", filename="a.txt")
    import_message(session, inbox_settings(), msg)
    attachment = session.query(InboundAttachment).first()
    assert attachment.stored is False
    assert attachment.blocked_reason == "metadata_only_phase11"
