from app.core.enums import InboundPartType
from app.db.models.inbound_message_part import InboundMessagePart
from app.services.clean_reply_extraction_service import CleanReplyExtractionService
from tests.phase11_helpers import import_message, sample_email


def test_clean_reply_extracted_and_quote_separated(session):
    _, message = import_message(session, msg=sample_email(body="Great\n\nOn Monday wrote:\nold"))
    clean, confidence = CleanReplyExtractionService(session).extract(message)
    parts = session.query(InboundMessagePart).all()
    assert clean == "Great"
    assert confidence > 0.5
    assert {part.part_type for part in parts} >= {
        InboundPartType.CLEAN_REPLY,
        InboundPartType.QUOTED_PREVIOUS_THREAD,
    }
