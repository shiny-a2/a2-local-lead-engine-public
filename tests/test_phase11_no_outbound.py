def test_phase11_has_no_outbound_actions():
    from app.services import mailbox_sync_service, reply_classification_service

    assert not hasattr(mailbox_sync_service, "SMTP")
    assert not hasattr(reply_classification_service, "send")


def test_no_ai_reply_text_generation():
    from app.services.reply_classification_service import ReplyClassificationService

    assert not hasattr(ReplyClassificationService, "generate_reply")
