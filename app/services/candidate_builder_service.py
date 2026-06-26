from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    CandidateSourceLinkType,
    CandidateStatus,
    ManualReviewType,
    NormalizationOperation,
    NormalizationRunStatus,
    VerificationReadiness,
)
from app.core.run_context import new_run_id
from app.db.models.campaign import Campaign
from app.db.models.candidate_alias import CandidateAlias
from app.db.models.candidate_business import CandidateBusiness
from app.db.models.candidate_category import CandidateCategory
from app.db.models.candidate_source_link import CandidateSourceLink
from app.db.models.normalization_run import NormalizationRun
from app.db.models.normalized_location import NormalizedLocation
from app.db.models.raw_source_record import RawSourceRecord
from app.db.models.source_run import SourceRun
from app.services.chain_risk_service import ChainRiskService
from app.services.manual_review_service import ManualReviewService
from app.services.normalization_service import NormalizationService


class CandidateBuilderService:
    def __init__(self, session: Session):
        self.session = session
        self.normalizer = NormalizationService()

    def start_run(
        self,
        operation: NormalizationOperation,
        *,
        campaign_slug: str | None = None,
        source_run_id: str | None = None,
        dry_run: bool = True,
    ) -> NormalizationRun:
        campaign = (
            self.session.scalar(select(Campaign).where(Campaign.slug == campaign_slug))
            if campaign_slug
            else None
        )
        source_run = (
            self.session.scalar(select(SourceRun).where(SourceRun.run_id == source_run_id))
            if source_run_id
            else None
        )
        run = NormalizationRun(
            run_id=new_run_id(),
            campaign_id=campaign.id if campaign else None,
            source_run_id=source_run.id if source_run else None,
            operation=operation,
            dry_run=dry_run,
        )
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def raw_records(
        self, source_run_id: str | None, limit: int | None = None
    ) -> list[RawSourceRecord]:
        query = select(RawSourceRecord).order_by(RawSourceRecord.id)
        if source_run_id:
            source_run = self.session.scalar(
                select(SourceRun).where(SourceRun.run_id == source_run_id)
            )
            if source_run:
                query = query.where(RawSourceRecord.source_run_id == source_run.id)
        if limit:
            query = query.limit(limit)
        return list(self.session.scalars(query).all())

    def build_from_raw(
        self,
        raw_records: list[RawSourceRecord],
        run: NormalizationRun,
        *,
        commit: bool,
    ) -> list[CandidateBusiness]:
        if not commit:
            run.status = NormalizationRunStatus.DRY_RUN_ONLY
            run.input_raw_count = len(raw_records)
            run.finished_at = datetime.now(UTC)
            self.session.commit()
            return []
        candidates: list[CandidateBusiness] = []
        review = ManualReviewService(self.session)
        for raw in raw_records:
            name = self.normalizer.normalize_name(raw.raw_name)
            category = self.normalizer.canonicalize_category(
                raw.raw_category, raw.source_name.value
            )
            geo_hash = self.normalizer.geo_hash(raw.raw_lat, raw.raw_lng)
            # Many OSM POIs omit addr:city / addr:country tags. Fall back to the queried
            # location recorded on the source run so the quality gate is not starved of a city.
            source_city = raw.source_run.city if raw.source_run else None
            source_country = raw.source_run.country if raw.source_run else None
            resolved_city = raw.raw_city or source_city or ""
            resolved_country = raw.raw_country or source_country or ""
            if not name.normalized_name or not category:
                run.rejected_count += 1
                continue
            fingerprint = self.normalizer.identity_fingerprint(
                {
                    "normalized_name": name.normalized_name,
                    "canonical_category": category,
                    "city": raw.raw_city,
                    "suburb": raw.raw_suburb,
                    "geo_hash": geo_hash,
                }
            )
            existing = self.session.scalar(
                select(CandidateBusiness).where(
                    CandidateBusiness.candidate_identity_fingerprint == fingerprint
                )
            )
            if existing:
                candidate = existing
                run.candidate_updated_count += 1
                link_type = CandidateSourceLinkType.SUPPORTING_SOURCE
            else:
                chain_score, chain_flags = ChainRiskService().score_raw([raw])
                candidate = CandidateBusiness(
                    campaign_id=run.campaign_id,
                    candidate_identity_fingerprint=fingerprint,
                    canonical_name=name.canonical_name,
                    display_name=name.display_name,
                    normalized_name=name.normalized_name,
                    canonical_category=category,
                    city=resolved_city,
                    suburb=raw.raw_suburb,
                    country=resolved_country,
                    address_line=raw.raw_address,
                    lat=raw.raw_lat,
                    lng=raw.raw_lng,
                    geo_hash=geo_hash,
                    geo_confidence=0.9 if raw.raw_lat and raw.raw_lng else 0.4,
                    identity_confidence=0.8,
                    category_confidence=0.8,
                    chain_risk_score=chain_score,
                    generic_name_risk_score=name.generic_risk_score,
                    verification_readiness_status=VerificationReadiness.NOT_READY_LOW_QUALITY,
                    status=CandidateStatus.CANDIDATE_CREATED,
                    created_from_run_id=run.run_id,
                )
                self.session.add(candidate)
                self.session.flush()
                run.candidate_created_count += 1
                link_type = CandidateSourceLinkType.PRIMARY_SOURCE
                if name.generic_risk_score >= 80:
                    review.create(
                        ManualReviewType.GENERIC_NAME_RISK,
                        "Generic name requires stronger evidence before merging.",
                        candidate_business_id=candidate.id,
                        evidence={"raw_record_id": raw.id},
                    )
                    run.manual_review_count += 1
                if chain_score >= 70:
                    review.create(
                        ManualReviewType.CHAIN_RISK,
                        "Chain or branch-like signal blocks auto-merge.",
                        candidate_business_id=candidate.id,
                        evidence={"risk_flags": chain_flags},
                    )
                    run.manual_review_count += 1
            self.session.add(
                CandidateSourceLink(
                    candidate_business_id=candidate.id,
                    raw_source_record_id=raw.id,
                    source_name=raw.source_name,
                    link_type=link_type,
                    match_score=100,
                    match_reasons_json=["created_from_raw_source_record"],
                    risk_flags_json=[],
                )
            )
            self.session.add(
                CandidateAlias(
                    candidate_business_id=candidate.id,
                    alias=raw.raw_name or candidate.display_name,
                    normalized_alias=name.normalized_name,
                    source_name=raw.source_name,
                    confidence=0.8,
                )
            )
            self.session.add(
                NormalizedLocation(
                    candidate_business_id=candidate.id,
                    raw_address=raw.raw_address,
                    normalized_address=self.normalizer.normalize_address(raw.raw_address),
                    city=resolved_city,
                    suburb=raw.raw_suburb,
                    country=resolved_country,
                    lat=raw.raw_lat,
                    lng=raw.raw_lng,
                    geo_hash=geo_hash,
                    confidence=0.9 if raw.raw_lat and raw.raw_lng else 0.5,
                    source_name=raw.source_name,
                )
            )
            self.session.add(
                CandidateCategory(
                    candidate_business_id=candidate.id,
                    raw_category=raw.raw_category,
                    canonical_category=category,
                    source_name=raw.source_name,
                    confidence=0.8,
                )
            )
            candidates.append(candidate)
        run.input_raw_count = len(raw_records)
        run.status = (
            NormalizationRunStatus.COMPLETED_WITH_WARNINGS
            if run.manual_review_count
            else NormalizationRunStatus.COMPLETED
        )
        run.finished_at = datetime.now(UTC)
        self.session.commit()
        return candidates
