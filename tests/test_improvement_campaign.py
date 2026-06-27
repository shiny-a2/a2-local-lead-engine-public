import json

from app.services.email_writer_service import EmailWriterService
from app.settings import Settings


class _Run:
    id = 1


class _Candidate:
    id = 1
    display_name = "Glow Beauty Studio"
    canonical_category = "beauty_salon"
    suburb = "Ponsonby"
    city = "Auckland"


def _service():
    return EmailWriterService(session=None, settings=Settings())


def test_improvement_input_is_improvement_lane():
    gi = _service()._improvement_input(_Run(), _Candidate(), "https://glowstudio.co.nz")
    assert gi.input_snapshot_json["campaign_lane"] == "IMPROVEMENT"
    assert gi.input_snapshot_json["website_url"] == "https://glowstudio.co.nz"
    assert gi.phase6_decision_id is None
    types = {ev["type"] for ev in gi.verified_evidence_json}
    assert types == {"business_name", "local_context"}


def test_local_improvement_draft_mentions_business_and_does_not_say_no_website():
    svc = _service()
    gi = svc._improvement_input(_Run(), _Candidate(), "https://glowstudio.co.nz")
    drafts = json.loads(svc._local_improvement_json(gi, "https://glowstudio.co.nz"))["drafts"]
    assert len(drafts) == 2
    for d in drafts:
        assert "Glow Beauty Studio" in d["body"]
        assert "{{unsubscribe_url}}" in d["body"]
        # improvement pitch must NOT claim the business lacks a website
        assert "you don't have a website" not in d["body"].lower()
        assert "!" not in d["body"]
