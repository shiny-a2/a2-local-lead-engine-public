from app.db.models.reply_draft_suggestion import ReplyDraftSuggestion
from app.services.reply_draft_suggestion_service import ReplyDraftSuggestionService
from app.settings import Settings
from tests.phase12_helpers import build_opportunity_from_body


def test_disabled_by_default(session):
    _, _, _, opp = build_opportunity_from_body(session, "yes interested")
    row = ReplyDraftSuggestionService(session, Settings()).create_optional(opp)
    assert row is None


def test_enabled_internal_only_needs_human_edit(session):
    _, _, _, opp = build_opportunity_from_body(session, "yes interested")
    row = ReplyDraftSuggestionService(
        session, Settings(phase12_allow_reply_draft_suggestions=True)
    ).create_optional(opp)
    assert row.status.value == "NEEDS_HUMAN_EDIT"
    assert row.risk_flags_json["send_ready"] is False
    assert session.query(ReplyDraftSuggestion).count() >= 1
