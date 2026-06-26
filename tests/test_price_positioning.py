from app.core.enums import PriceVisibility
from app.services.price_positioning_service import PricePositioningService


def test_soft_price_positioning_no_final_quote():
    row = PricePositioningService().build(1, 1)
    assert row.price_visibility == PriceVisibility.MENTION_LATER
    assert "final quote" in row.blocked_language_json
    assert any("starter" in text for text in row.recommended_language_json)
