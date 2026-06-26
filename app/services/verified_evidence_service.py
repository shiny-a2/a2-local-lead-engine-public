from app.core.enums import Phase4WebsiteStatus
from app.db.models.candidate_business import CandidateBusiness


class VerifiedEvidenceService:
    def from_web_status(self, candidate: CandidateBusiness, status: Phase4WebsiteStatus, urls: list[str] | None = None) -> list[dict]:
        mapping = {
            Phase4WebsiteStatus.SOCIAL_ONLY: "verified_social_only",
            Phase4WebsiteStatus.DIRECTORY_ONLY: "verified_directory_only",
            Phase4WebsiteStatus.NO_WEBSITE_PROBABLE: "verified_no_dedicated_website_probable",
            Phase4WebsiteStatus.WEAK_WEBSITE_FOUND: "verified_weak_website",
            Phase4WebsiteStatus.WEBSITE_FOUND_OFFICIAL: "verified_official_website_found",
        }
        evidence_type = mapping.get(status)
        rows = [
            {
                "evidence_type": "verified_business_local_context",
                "evidence_value": f"{candidate.display_name} in {candidate.city}",
                "evidence_source": "phase4_verification",
                "confidence": 0.8,
                "allowed_for_future_copy": True,
                "requires_verification": False,
                "risk_flag": None,
                "supporting_urls_json": urls or [],
                "supporting_candidate_evidence_ids_json": [],
            }
        ]
        if evidence_type:
            rows.append(
                {
                    "evidence_type": evidence_type,
                    "evidence_value": status.value,
                    "evidence_source": "phase4_verification",
                    "confidence": 0.75,
                    "allowed_for_future_copy": evidence_type != "verified_official_website_found",
                    "requires_verification": False,
                    "risk_flag": None,
                    "supporting_urls_json": urls or [],
                    "supporting_candidate_evidence_ids_json": [],
                }
            )
        return rows
