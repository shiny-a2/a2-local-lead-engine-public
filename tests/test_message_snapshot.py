from app.db.models.email_draft_variant import EmailDraftVariant
from app.db.models.sender_provider_config import SenderProviderConfig
from app.services.message_snapshot_service import MessageSnapshotService
from tests.phase10_helpers import make_phase10_queue_item


def test_message_snapshot_created_original_not_mutated(session):
    _, _, item, settings = make_phase10_queue_item(session)
    draft = session.get(EmailDraftVariant, item.email_draft_variant_id)
    original = draft.body_text
    provider = session.get(SenderProviderConfig, item.sender_profile_id)
    snap = MessageSnapshotService(session, settings).create(item, provider, "https://u")
    assert snap.final_subject_snapshot
    assert snap.final_body_snapshot
    assert snap.final_message_hash
    assert draft.body_text == original
