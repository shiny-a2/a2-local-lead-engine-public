from app.services.draft_precheck_service import DraftPrecheckService
from app.settings import Settings


def _body(extra=""):
    return (
        "I was looking at Example Studio around Ponsonby and noticed the public web presence could point customers more directly. "
        "One small idea is a lightweight owned web page for services and contact. "
        "It could start simple and grow only if useful. "
        "The page could include the key service details, a gentle enquiry path, and a clear way for local customers to take the next step without a complicated setup. "
        "I am Amirali Yaghouti, and I build simple local-business web systems. "
        f"Would a quick idea be useful? {{{{unsubscribe_url}}}} {extra}"
    )


def test_precheck_passes_safe_draft():
    row = DraftPrecheckService().check(1, "A simple website idea", _body(), 2, Settings())
    assert row.precheck_status.value == "PASSED"


def test_precheck_blocks_forbidden_claims():
    row = DraftPrecheckService().check(1, "Guaranteed savings", _body("guaranteed"), 2, Settings())
    assert row.precheck_status.value == "FAILED"
    assert "blocked_words_ok" in row.risk_flags_json
