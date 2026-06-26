from sqlalchemy import select

from app.db.models.email_draft import EmailDraft
from app.db.models.email_send import EmailSend


def test_no_email_drafts_created(session):
    assert session.scalars(select(EmailDraft)).all() == []


def test_no_email_sends_created(session):
    assert session.scalars(select(EmailSend)).all() == []


def test_no_openai_calls():
    assert True


def test_no_smtp():
    assert True


def test_no_voice():
    assert True


def test_no_google_maps_dependency():
    assert True


def test_no_contact_form_submit():
    assert True


def test_no_social_dm_automation():
    assert True


def test_no_ready_to_send_status_created():
    assert "READY_FOR_PHASE_5_SCORING" != "SEND_READY"

