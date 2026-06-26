from app.core.enums import ReplyClassificationValue
from app.services.reply_classification_service import ReplyClassificationService
from tests.phase11_helpers import inbox_settings


def test_reply_classification_categories(session):
    service = ReplyClassificationService(session, inbox_settings())
    assert service.classify_text("", "what is the price?")[0] == ReplyClassificationValue.ASKING_PRICE
    assert service.classify_text("", "tell me more details")[0] == ReplyClassificationValue.ASKING_DETAILS
    assert service.classify_text("", "not interested")[0] == ReplyClassificationValue.NOT_INTERESTED
    assert service.classify_text("", "wrong contact")[0] == ReplyClassificationValue.WRONG_CONTACT
    assert service.classify_text("", "yes sounds good")[0] == ReplyClassificationValue.POSITIVE_INTEREST
