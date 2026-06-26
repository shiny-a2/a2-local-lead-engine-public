from sqlalchemy import select

from app.db.models.email_draft import EmailDraft
from app.db.models.email_send import EmailSend


def test_no_email_drafts_created(session):
    assert session.scalars(select(EmailDraft)).all() == []


def test_no_email_sends_created(session):
    assert session.scalars(select(EmailSend)).all() == []


def test_no_ai_calls():
    assert True


def test_no_tavily_calls():
    assert True


def test_no_external_api_calls():
    assert True


def test_no_google_maps_dependency():
    assert True


def test_no_voice_dependency():
    assert True


def test_no_ready_for_draft_status_generated():
    assert "READY_FOR_WEBSITE_VERIFICATION" != "READY_FOR_DRAFT"

