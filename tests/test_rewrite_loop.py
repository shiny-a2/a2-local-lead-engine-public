"""The text-rewrite-retry loop: a draft rejected for its WORDS is rewritten (bounded) instead of
being burned; a draft rejected for its RECIPIENT is never reworded-and-resent."""
from app.core.enums import EmailDraftVariantStatus
from app.db.models.email_draft_variant import EmailDraftVariant
from app.services.email_writer_service import EmailWriterService
from app.services.rejection_taxonomy_service import RejectionTaxonomyService
from app.settings import Settings
from tests.phase7_helpers import make_phase7_ready_candidate


def _rewrite_settings(**over):
    base = dict(email_drafting_enabled=True, email_local_writer_enabled=True, email_rewrite_enabled=True)
    base.update(over)
    return Settings(**base)


def test_taxonomy_contact_dominant():
    t = RejectionTaxonomyService()
    assert t.classify_qa(["recipient email does not match the business name and location"]) == "CONTACT_FIXABLE"
    assert t.classify_qa(["domain does not match country (Australia vs New Zealand)"]) == "CONTACT_FIXABLE"
    # text + contact mixed -> CONTACT-dominant (never reword + resend to a wrong recipient)
    assert t.classify_qa(["the tone is too salesy and the recipient is a different business"]) == "CONTACT_FIXABLE"
    assert t.classify_qa([]) == "CONTACT_FIXABLE"  # unknown defaults to the safe side


def test_taxonomy_text_fixable():
    t = RejectionTaxonomyService()
    assert t.classify_judge([{"finding_type": "UNSUPPORTED_CLAIM", "message": "claim not supported by evidence"}]) == "TEXT_FIXABLE"
    assert t.classify_qa(["the email text is too generic and not specific to this business"]) == "TEXT_FIXABLE"


def test_rewrite_creates_bounded_new_variant(session):
    campaign, _ = make_phase7_ready_candidate(session)
    writer = EmailWriterService(session, _rewrite_settings())
    writer.generate(campaign.slug, None, 10, commit=True)
    draft = session.query(EmailDraftVariant).first()
    draft.status = EmailDraftVariantStatus.AWAITING_REWRITE
    session.commit()
    before = session.query(EmailDraftVariant).count()
    produced = writer.rewrite_awaiting_drafts(campaign.slug, 10, commit=True)
    assert produced == 1
    assert session.query(EmailDraftVariant).count() == before + 1
    new = session.query(EmailDraftVariant).order_by(EmailDraftVariant.id.desc()).first()
    assert new.rewrite_attempt == 1
    assert new.origin_email_draft_variant_id == draft.id
    session.refresh(draft)
    assert draft.status == EmailDraftVariantStatus.JUDGED  # superseded, not burned


def test_rewrite_respects_attempt_cap(session):
    campaign, _ = make_phase7_ready_candidate(session)
    writer = EmailWriterService(session, _rewrite_settings(email_rewrite_max_attempts=2))
    writer.generate(campaign.slug, None, 10, commit=True)
    draft = session.query(EmailDraftVariant).first()
    draft.status = EmailDraftVariantStatus.AWAITING_REWRITE
    draft.rewrite_attempt = 2  # already at the cap
    session.commit()
    assert writer.rewrite_awaiting_drafts(campaign.slug, 10, commit=True) == 0


def test_rewrite_noop_when_disabled(session):
    campaign, _ = make_phase7_ready_candidate(session)
    writer = EmailWriterService(session, Settings(email_drafting_enabled=True, email_local_writer_enabled=True))
    writer.generate(campaign.slug, None, 10, commit=True)
    draft = session.query(EmailDraftVariant).first()
    draft.status = EmailDraftVariantStatus.AWAITING_REWRITE
    session.commit()
    assert writer.rewrite_awaiting_drafts(campaign.slug, 10, commit=True) == 0
