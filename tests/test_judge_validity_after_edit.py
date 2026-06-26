from app.services.final_pre_send_review_service import FinalPreSendReviewService
from app.services.manual_edit_service import ManualEditService
from tests.phase9_helpers import make_phase9_queue_item


def test_minor_edit_allows_final_check(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    ManualEditService(session, settings).create_version(item.id, "A simple website idea", "I was looking at Example Phase Six Studio around Ponsonby and noticed a simple owned page could make useful details easier to find. A lightweight services and booking idea could keep the customer action path in one calm place, without changing anything else. It can start small and only grow if it proves useful. I am Amirali Yaghouti, and I build simple local-business web systems. Would a quick idea for a simple first version be useful? {{unsubscribe_url}}", "Amirali", "small edit")
    check = FinalPreSendReviewService(session, settings).run(item.id)
    assert check.judge_validity_ok is True


def test_major_edit_new_claim_requires_rejudge(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    ManualEditService(session, settings).create_version(item.id, "Subject", "Guaranteed savings and stop paying commissions. I am Amirali. {{unsubscribe_url}}?", "Amirali", "claim")
    check = FinalPreSendReviewService(session, settings).run(item.id)
    assert check.judge_validity_ok is False
    assert check.check_status.value == "FAILED"
