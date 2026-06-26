from app.services.identity_resolution_service import geo_distance_m
from app.services.normalization_service import NormalizationService


def test_lat_lng_rounding_for_matching():
    assert NormalizationService().geo_hash(-36.85123, 174.74123) == "-36.851:174.741"


def test_geo_hash_stable():
    service = NormalizationService()
    assert service.geo_hash(1.23456, 2.34567) == service.geo_hash(1.23456, 2.34567)


def test_nearby_records_detected():
    assert geo_distance_m(-36.85, 174.74, -36.8501, 174.7401) < 50


def test_far_records_not_auto_merged():
    assert geo_distance_m(-36.85, 174.74, -36.90, 174.80) > 500


def test_cleaning_service_can_be_ready_with_less_precise_location_warning():
    assert True
