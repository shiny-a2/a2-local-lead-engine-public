from app.services.subject_line_service import SubjectLineService
from app.settings import Settings


def test_subject_short_and_safe():
    row = SubjectLineService().generate("Example Barber", "A", Settings())
    assert row["word_count"] <= 8
    assert row["allowed_for_judge"] is True


def test_subject_blocks_clickbait_terms():
    service = SubjectLineService()
    assert "guaranteed" in service.blocked
