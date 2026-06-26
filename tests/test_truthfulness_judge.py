from app.services.email_truthfulness_service import EmailTruthfulnessService


def test_no_website_conservative_claim_allowed_when_permission_exists():
    score, flags = EmailTruthfulnessService().score("I couldn't find a dedicated website in the public sources I checked.")
    assert score >= 90
    assert flags == []


def test_absolute_no_website_blocked():
    score, flags = EmailTruthfulnessService().score("You don't have a website.")
    assert score < 90
    assert "absolute_no_website_claim" in flags


def test_social_only_claim_requires_evidence_style():
    score, _ = EmailTruthfulnessService().score("It looks like customers may mostly find you through social listings.")
    assert score >= 90


def test_unsupported_booking_economic_claim_blocked():
    score, flags = EmailTruthfulnessService().score("This will guarantee more bookings and save thousands.")
    assert score < 90
    assert "guaranteed_result_claim" in flags
