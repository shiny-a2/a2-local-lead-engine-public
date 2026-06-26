from app.services.normalization_service import NormalizationService


def test_apostrophe_normalization():
    assert NormalizationService().normalize_name("Bob’s Barber").normalized_name == "bob's barber"


def test_legal_suffix_removal_for_matching_only():
    item = NormalizationService().normalize_name("Example Limited")
    assert item.display_name == "Example Limited"
    assert item.normalized_name == "example"


def test_display_name_preserved():
    assert NormalizationService().normalize_name(" A&B Studio ").display_name == "A&B Studio"


def test_generic_names_flagged():
    assert NormalizationService().normalize_name("Barber Shop").generic_risk_score >= 80


def test_ampersand_normalization_for_matching_only():
    item = NormalizationService().normalize_name("A & B Hair")
    assert item.display_name == "A & B Hair"
    assert item.normalized_name == "a and b hair"

