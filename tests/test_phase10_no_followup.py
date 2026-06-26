from tests.phase10_helpers import make_phase10_queue_item, send_once


def test_no_followup_inbox_ai_voice_social_contact_form_actions(session):
    _, _, item, _ = make_phase10_queue_item(session)
    run = send_once(session, item)
    assert run.metadata_json["followups"] == "not-implemented"
    assert not hasattr(run, "inbox_sync")
    assert not hasattr(run, "ai_reply_processing")
