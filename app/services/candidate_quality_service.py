from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import (
    CandidateQualityDecision,
    CandidateStatus,
    VerificationReadiness,
)
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_quality_report import CandidateQualityReport


class CandidateQualityService:
    def __init__(self, session: Session | None = None):
        self.session = session

    def score(self, candidate: CandidateBusiness) -> dict[str, Any]:
        identity = 100.0 if candidate.normalized_name else 0.0
        location = 100.0 if candidate.lat and candidate.lng else 70.0 if candidate.suburb else 35.0
        if candidate.canonical_category == "cleaning_service" and location >= 35:
            location = max(location, 65.0)
        category = 100.0 if candidate.canonical_category else 0.0
        source_diversity = min(100.0, len(candidate.source_links) * 50.0)
        evidence_score = min(100.0, len(candidate.evidence) * 20.0)
        contact_hint = 50.0
        risk = max(
            candidate.chain_risk_score,
            candidate.duplicate_risk_score,
            candidate.generic_name_risk_score,
        )
        quality = (
            identity * 0.25
            + location * 0.20
            + category * 0.20
            + source_diversity * 0.15
            + evidence_score * 0.10
            + contact_hint * 0.10
            - risk * 0.25
        )
        quality = max(0.0, min(100.0, quality))
        decision = self.decision(candidate, quality)
        return {
            "quality_score": quality,
            "identity_score": identity,
            "location_score": location,
            "category_score": category,
            "contact_hint_score": contact_hint,
            "source_diversity_score": source_diversity,
            "personalization_evidence_score": evidence_score,
            "risk_score": risk,
            "readiness_decision": decision.value,
            "quality_notes_json": {"score_type": "data_quality_not_sales_lead_score"},
        }

    def decision(
        self, candidate: CandidateBusiness, quality: float
    ) -> CandidateQualityDecision:
        if not candidate.normalized_name:
            return CandidateQualityDecision.NEEDS_MORE_DATA
        if not candidate.city or not candidate.country:
            return CandidateQualityDecision.NEEDS_MORE_DATA
        if candidate.chain_risk_score >= 70 or candidate.duplicate_risk_score >= 70:
            return CandidateQualityDecision.NEEDS_MANUAL_REVIEW
        if quality >= 80:
            return CandidateQualityDecision.READY_FOR_PHASE_4
        if quality >= 65:
            return CandidateQualityDecision.READY_FOR_PHASE_4_WITH_WARNINGS
        if quality >= 50:
            return CandidateQualityDecision.NEEDS_MANUAL_REVIEW
        return CandidateQualityDecision.NEEDS_MORE_DATA

    def apply(self, candidate: CandidateBusiness) -> CandidateQualityReport:
        values = self.score(candidate)
        decision = CandidateQualityDecision(str(values["readiness_decision"]))
        if decision == CandidateQualityDecision.READY_FOR_PHASE_4:
            candidate.status = CandidateStatus.READY_FOR_WEBSITE_VERIFICATION
            candidate.verification_readiness_status = VerificationReadiness.READY
        elif decision == CandidateQualityDecision.READY_FOR_PHASE_4_WITH_WARNINGS:
            candidate.status = CandidateStatus.READY_FOR_WEBSITE_VERIFICATION
            candidate.verification_readiness_status = VerificationReadiness.READY_WITH_WARNINGS
        elif decision == CandidateQualityDecision.NEEDS_MANUAL_REVIEW:
            candidate.status = CandidateStatus.NEEDS_MANUAL_REVIEW
            candidate.verification_readiness_status = (
                VerificationReadiness.NOT_READY_AMBIGUOUS_IDENTITY
            )
        else:
            candidate.status = CandidateStatus.NEEDS_MORE_DATA
            candidate.verification_readiness_status = VerificationReadiness.NOT_READY_LOW_QUALITY
        candidate.data_quality_score = float(values["quality_score"])
        report = CandidateQualityReport(
            candidate_business_id=candidate.id,
            quality_score=float(values["quality_score"]),
            identity_score=float(values["identity_score"]),
            location_score=float(values["location_score"]),
            category_score=float(values["category_score"]),
            contact_hint_score=float(values["contact_hint_score"]),
            source_diversity_score=float(values["source_diversity_score"]),
            personalization_evidence_score=float(values["personalization_evidence_score"]),
            risk_score=float(values["risk_score"]),
            readiness_decision=decision,
            quality_notes_json=dict(values["quality_notes_json"]),
        )
        if self.session is None:
            return report
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report
