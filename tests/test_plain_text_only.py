import pytest

from app.services.message_snapshot_service import MessageSnapshotService
from tests.phase10_helpers import make_phase10_queue_item


def test_html_blocks_snapshot(session):
    _, _, item, settings = make_phase10_queue_item(session)
    from app.db.models.email_draft_variant import EmailDraftVariant
    from app.db.models.sender_provider_config import SenderProviderConfig

    draft = session.get(EmailDraftVariant, item.email_draft_variant_id)
    draft.body_text = "<html>{{unsubscribe_url}}</html>"
    provider = session.get(SenderProviderConfig, item.sender_profile_id)
    with pytest.raises(ValueError):
        MessageSnapshotService(session, settings).create(item, provider, "https://u")
