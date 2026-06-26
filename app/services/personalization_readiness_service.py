from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.claim_permission import ClaimPermission
from app.db.models.verified_personalization_evidence import VerifiedPersonalizationEvidence


class PersonalizationReadinessService:
    safe_evidence = {
        "verified_social_only",
        "verified_directory_only",
        "verified_no_dedicated_website_probable",
        "verified_weak_website",
        "verified_business_local_context",
        "verified_category_context",
    }

    def __init__(self, session: Session):
        self.session = session

    def evaluate(self, candidate_id: int) -> dict[str, object]:
        evidence = self.session.scalars(
            select(VerifiedPersonalizationEvidence).where(
                VerifiedPersonalizationEvidence.candidate_business_id == candidate_id,
                VerifiedPersonalizationEvidence.allowed_for_future_copy.is_(True),
            )
        ).all()
        permissions = self.session.scalars(
            select(ClaimPermission).where(
                ClaimPermission.candidate_business_id == candidate_id,
                ClaimPermission.allowed.is_(True),
            )
        ).all()
        safe_count = sum(1 for row in evidence if row.evidence_type in self.safe_evidence)
        score = min(100.0, safe_count * 25.0 + len(permissions) * 20.0)
        passed = safe_count > 0 and bool(permissions)
        return {
            "passed": passed,
            "score": score,
            "evidence_count": len(evidence),
            "safe_evidence_count": safe_count,
            "claim_permission_count": len(permissions),
        }
