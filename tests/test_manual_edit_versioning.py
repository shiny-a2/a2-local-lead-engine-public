from app.core.enums import HumanReviewAuditAction
from app.db.models.email_manual_edit_version import EmailManualEditVersion
from app.db.models.human_review_audit_event import HumanReviewAuditEvent
from app.services.manual_edit_service import ManualEditService
from tests.phase9_helpers import make_phase9_queue_item


def test_edit_creates_new_version_and_preserves_previous(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    service = ManualEditService(session, settings)
    v1 = service.create_version(item.id, "Subject one", "Body one with Amirali and {{unsubscribe_url}}?", "Amirali", "Reason")
    v2 = service.create_version(item.id, "Subject two", "Body two with Amirali and {{unsubscribe_url}}?", "Amirali", "Reason")
    assert v2.previous_version_id == v1.id
    assert session.query(EmailManualEditVersion).count() == 2


def test_diff_and_audit_event_created(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    version = ManualEditService(session, settings).create_version(item.id, "Subject", "Changed body with Amirali and {{unsubscribe_url}}?", "Amirali", "Reason")
    assert version.diff_json
    assert session.query(HumanReviewAuditEvent).filter_by(action=HumanReviewAuditAction.EDITED).count() == 1


def test_major_edit_or_new_claim_requires_rejudge(session):
    _, _, _, item, settings = make_phase9_queue_item(session)
    version = ManualEditService(session, settings).create_version(item.id, "Subject", "You don't have a website. I am Amirali. {{unsubscribe_url}}?", "Amirali", "Reason")
    assert version.requires_rejudge is True
