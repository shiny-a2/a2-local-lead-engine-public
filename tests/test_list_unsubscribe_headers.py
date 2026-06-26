from email.message import EmailMessage

from app.services.list_unsubscribe_header_service import ListUnsubscribeHeaderService


def test_list_unsubscribe_headers_created():
    msg = EmailMessage()
    ListUnsubscribeHeaderService().add(msg, "https://example.com/unsubscribe?token=x")
    assert "List-Unsubscribe" in msg
    assert msg["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
