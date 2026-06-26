from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.candidate_personalization_evidence import CandidatePersonalizationEvidence
from app.db.models.candidate_source_link import CandidateSourceLink
from app.db.models.raw_personalization_evidence import RawPersonalizationEvidence

SAFE_COPY_TYPES = {
    "business_name",
    "category_hint",
    "suburb_hint",
    "local_area_hint",
    "service_category_hint",
}


class CandidateEvidenceService:
    def __init__(self, session: Session):
        self.session = session

    def consolidate_for_candidate(self, candidate_id: int, commit: bool = True) -> list[dict]:
        links = self.session.scalars(
            select(CandidateSourceLink).where(
                CandidateSourceLink.candidate_business_id == candidate_id
            )
        ).all()
        raw_ids = [link.raw_source_record_id for link in links]
        raw_evidence = self.session.scalars(
            select(RawPersonalizationEvidence).where(
                RawPersonalizationEvidence.raw_source_record_id.in_(raw_ids)
            )
        ).all()
        grouped: dict[tuple[str, str], list[RawPersonalizationEvidence]] = defaultdict(list)
        for item in raw_evidence:
            grouped[(item.evidence_type, item.evidence_value)].append(item)
        rows: list[dict] = []
        for (evidence_type, evidence_value), items in grouped.items():
            allowed = evidence_type in SAFE_COPY_TYPES
            if evidence_type in {
                "website_field_missing",
                "raw_email",
                "raw_phone",
                "email_present_raw",
            }:
                allowed = False
            row = {
                "candidate_business_id": candidate_id,
                "evidence_type": evidence_type,
                "evidence_value": evidence_value,
                "evidence_source": ",".join(sorted({item.evidence_source for item in items})),
                "confidence": max(item.confidence or 0.5 for item in items),
                "allowed_for_future_copy": allowed,
                "requires_verification": True,
                "risk_flag": next((item.risk_flag for item in items if item.risk_flag), None),
                "supporting_raw_record_ids_json": sorted(
                    {item.raw_source_record_id for item in items}
                ),
            }
            rows.append(row)
            if commit:
                self.session.add(CandidatePersonalizationEvidence(**row))
        if commit:
            self.session.commit()
        return rows
