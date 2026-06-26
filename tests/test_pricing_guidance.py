from app.db.models.pricing_guidance_record import PricingGuidanceRecord
from tests.phase12_helpers import build_opportunity_from_body


def test_price_guidance_is_manual_only(session):
    build_opportunity_from_body(session, "how much does it cost?")
    guidance = session.query(PricingGuidanceRecord).first()
    assert guidance.manual_quote_required is True
    assert guidance.show_price_to_user is False
    assert guidance.scope_questions_json["questions"]
    assert "fixed final quote" in guidance.blocked_price_claims_json["blocked"]
