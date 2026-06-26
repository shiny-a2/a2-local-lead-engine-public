from fastapi import APIRouter, Query
from sqlalchemy import select

from app.db.models.raw_personalization_evidence import RawPersonalizationEvidence
from app.db.models.raw_source_record import RawSourceRecord
from app.db.models.source_run import SourceRun
from app.db.session import make_session_factory
from app.settings import get_settings

router = APIRouter()


@router.get("/sources")
def sources() -> list[dict[str, object]]:
    settings = get_settings()
    enabled = settings.live_api_calls_enabled and settings.lead_collection_enabled
    return [
        {
            "source_name": "geoapify",
            "configured": bool(settings.geoapify_api_key),
            "enabled": enabled,
        },
        {"source_name": "osm_overpass", "configured": True, "enabled": enabled},
        {"source_name": "nzbn", "configured": bool(settings.nzbn_api_key), "enabled": enabled},
    ]


@router.get("/source-runs")
def source_runs() -> list[dict[str, object]]:
    with make_session_factory(get_settings())() as session:
        rows = session.scalars(select(SourceRun).order_by(SourceRun.id.desc())).all()
        return [
            {
                "run_id": row.run_id,
                "source_name": row.source_name.value,
                "operation": row.operation.value,
                "status": row.status.value,
                "dry_run": row.dry_run,
            }
            for row in rows
        ]


@router.get("/source-runs/{run_id}")
def source_run(run_id: str) -> dict[str, object]:
    with make_session_factory(get_settings())() as session:
        row = session.scalar(select(SourceRun).where(SourceRun.run_id == run_id))
        if row is None:
            return {"found": False}
        return {
            "found": True,
            "run_id": row.run_id,
            "source_name": row.source_name.value,
            "status": row.status.value,
            "fetched_count": row.fetched_count,
            "stored_count": row.stored_count,
            "skipped_count": row.skipped_count,
        }


@router.get("/raw-records")
def raw_records(source_run_id: str = Query()) -> list[dict[str, object]]:
    with make_session_factory(get_settings())() as session:
        run = session.scalar(select(SourceRun).where(SourceRun.run_id == source_run_id))
        if run is None:
            return []
        rows = session.scalars(
            select(RawSourceRecord).where(RawSourceRecord.source_run_id == run.id)
        ).all()
        return [
            {
                "id": row.id,
                "source_name": row.source_name.value,
                "record_type": row.record_type.value,
                "raw_name": row.raw_name,
                "raw_category": row.raw_category,
                "raw_city": row.raw_city,
                "raw_suburb": row.raw_suburb,
                "has_raw_email": bool(row.raw_email),
                "has_raw_website": bool(row.raw_website),
            }
            for row in rows
        ]


@router.get("/raw-personalization-evidence")
def raw_personalization_evidence(source_run_id: str = Query()) -> list[dict[str, object]]:
    with make_session_factory(get_settings())() as session:
        run = session.scalar(select(SourceRun).where(SourceRun.run_id == source_run_id))
        if run is None:
            return []
        rows = session.scalars(
            select(RawPersonalizationEvidence).where(
                RawPersonalizationEvidence.source_run_id == run.id
            )
        ).all()
        return [
            {
                "evidence_type": row.evidence_type,
                "evidence_source": row.evidence_source,
                "allowed_for_future_copy": row.allowed_for_future_copy,
                "requires_verification": row.requires_verification,
                "risk_flag": row.risk_flag,
            }
            for row in rows
        ]
