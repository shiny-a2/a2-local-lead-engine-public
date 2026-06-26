from app.core.enums import Phase4WebsiteStatus
from app.db.models.candidate_business import CandidateBusiness

BLOCKED_CLAIMS = [
    "You don't have a website.",
    "Your marketing is weak.",
    "You are losing customers.",
    "I saw you on Google Maps.",
]


class ClaimPermissionService:
    def permissions_for_status(self, candidate: CandidateBusiness, status: Phase4WebsiteStatus, confidence: float) -> list[dict]:
        rows = [
            {
                "claim_type": "blocked_no_website_absolute_claim",
                "allowed": False,
                "confidence": 1.0,
                "approved_phrasing": None,
                "blocked_phrasing_json": BLOCKED_CLAIMS,
                "evidence_json": {"rule": "absolute_or_aggressive_claim_blocked"},
            },
            {
                "claim_type": "blocked_google_maps_reference",
                "allowed": False,
                "confidence": 1.0,
                "approved_phrasing": None,
                "blocked_phrasing_json": ["I saw you on Google Maps."],
                "evidence_json": {"rule": "google_maps_prohibited"},
            },
        ]
        if status in {Phase4WebsiteStatus.NO_WEBSITE_PROBABLE, Phase4WebsiteStatus.NO_WEBSITE_CONFIRMED} and confidence >= 70:
            rows.append(
                {
                    "claim_type": "can_say_could_not_find_dedicated_website",
                    "allowed": True,
                    "confidence": confidence,
                    "approved_phrasing": f"I couldn't find a dedicated website for {candidate.display_name} in the public sources I checked.",
                    "blocked_phrasing_json": ["You don't have a website."],
                    "evidence_json": {"website_status": status.value},
                }
            )
        if status == Phase4WebsiteStatus.SOCIAL_ONLY:
            rows.append(
                {
                    "claim_type": "can_say_social_or_directory_presence",
                    "allowed": True,
                    "confidence": confidence,
                    "approved_phrasing": "I found social or directory presence, but not a dedicated website in the sources checked.",
                    "blocked_phrasing_json": [],
                    "evidence_json": {"website_status": status.value},
                }
            )
        return rows

