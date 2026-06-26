from app.core.enums import DomainClassification
from app.services.domain_classifier_service import DomainClassifierService


def test_social_domains_recognized():
    assert DomainClassifierService().classify("https://facebook.com/x") == DomainClassification.SOCIAL_DOMAIN


def test_directory_domains_recognized():
    assert DomainClassifierService().classify("https://yellow.co.nz/x") == DomainClassification.DIRECTORY_DOMAIN


def test_booking_marketplace_recognized():
    assert DomainClassifierService().classify("https://fresha.com/x") == DomainClassification.BOOKING_PLATFORM_DOMAIN
    assert DomainClassifierService().classify("https://trademe.co.nz/x") == DomainClassification.MARKETPLACE_DOMAIN


def test_official_candidate_domain_recognized():
    assert DomainClassifierService().classify("https://examplebarber.co.nz", "Example Barber") == DomainClassification.OFFICIAL_CANDIDATE_DOMAIN


def test_suspicious_parked_handled():
    assert DomainClassifierService().classify("https://parked-domain-for-sale.com") == DomainClassification.PARKED_DOMAIN

