from app.services.rewrite_brief_service import RewriteBriefService


def test_rewrite_brief_created_for_rewrite_required():
    brief = RewriteBriefService().build(
        1,
        2,
        3,
        [
            {"severity": "BLOCKER", "message": "Blocked phrase: guaranteed"},
            {"severity": "WARNING", "message": "Subject is too long."},
        ],
    )
    assert brief.rewrite_instructions_json
    assert "Blocked phrase: guaranteed" in brief.must_remove_json
    assert "Subject is too long." in brief.must_soften_json
    assert not hasattr(brief, "body_text")
