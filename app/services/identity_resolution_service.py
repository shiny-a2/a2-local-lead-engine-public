from dataclasses import dataclass
from difflib import SequenceMatcher
from math import atan2, cos, radians, sin, sqrt

from app.db.models.raw_source_record import RawSourceRecord
from app.services.normalization_service import NormalizationService


@dataclass(frozen=True)
class IdentityDecision:
    match_score: float
    decision: str
    reasons: list[str]
    risk_flags: list[str]


class IdentityResolutionService:
    def __init__(self):
        self.normalizer = NormalizationService()

    def score(self, left: RawSourceRecord, right: RawSourceRecord) -> IdentityDecision:
        score = 0.0
        reasons: list[str] = []
        risks: list[str] = []
        if (
            left.source_name == right.source_name
            and left.source_external_id == right.source_external_id
        ):
            score += 40
            reasons.append("same_source_external_id")
        left_name = self.normalizer.normalize_name(left.raw_name).normalized_name
        right_name = self.normalizer.normalize_name(right.raw_name).normalized_name
        similarity = SequenceMatcher(None, left_name, right_name).ratio()
        score += similarity * 45
        if similarity > 0.9:
            reasons.append("high_name_similarity")
        if left.raw_phone and left.raw_phone == right.raw_phone:
            score += 20
            reasons.append("exact_phone_match")
        if left.raw_website and left.raw_website == right.raw_website:
            score += 15
            reasons.append("exact_website_match")
        if left.raw_category and right.raw_category and left.raw_category == right.raw_category:
            score += 15
            reasons.append("same_raw_category")
        distance = geo_distance_m(left.raw_lat, left.raw_lng, right.raw_lat, right.raw_lng)
        if distance is not None:
            if distance < 50:
                score += 25
                reasons.append("strong_geo_match")
            elif distance < 150:
                score += 10
                reasons.append("possible_geo_match")
            elif distance > 500:
                score -= 25
                risks.append("far_location")
        if left.raw_category and right.raw_category and left.raw_category != right.raw_category:
            score -= 20
            risks.append("different_category")
        if self.normalizer.normalize_name(left.raw_name).generic_risk_score >= 80:
            risks.append("generic_name")
            score -= 10
        if any(term in left_name for term in ("group", "franchise", "branch")):
            risks.append("chain_risk")
            score -= 30
        if "far_location" in risks and similarity > 0.8:
            risks.append("possible_branch_split")
        if score >= 80 and not risks:
            decision = "AUTO_MERGE"
        elif score >= 60:
            decision = "NEEDS_MANUAL_REVIEW"
        else:
            decision = "SEPARATE"
        return IdentityDecision(max(0, min(100, score)), decision, reasons, risks)


def geo_distance_m(
    lat1: float | None, lng1: float | None, lat2: float | None, lng2: float | None
) -> float | None:
    if None in (lat1, lng1, lat2, lng2):
        return None
    assert lat1 is not None
    assert lng1 is not None
    assert lat2 is not None
    assert lng2 is not None
    radius = 6371000
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return radius * 2 * atan2(sqrt(a), sqrt(1 - a))
