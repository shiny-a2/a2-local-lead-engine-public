import json
from collections import Counter
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.raw_personalization_evidence import RawPersonalizationEvidence
from app.db.models.raw_source_record import RawSourceRecord
from app.db.models.source_request import SourceRequest
from app.db.models.source_run import SourceRun

RAW_ONLY_WARNING = (
    "This is raw source intake only. It does not confirm that a business has no website, "
    "does not authorize outreach, does not create send-ready leads, and does not generate "
    "email content. Missing website/contact data in a raw source does not prove absence."
)


class SourceQualityService:
    def __init__(self, session: Session):
        self.session = session

    def quality_for_record(self, record: RawSourceRecord) -> dict[str, object]:
        return {
            "has_name": bool(record.raw_name),
            "has_category": bool(record.raw_category),
            "has_location": bool(record.raw_lat and record.raw_lng),
            "has_contact_hint": bool(record.raw_phone or record.raw_email or record.raw_website),
            "has_website_field": bool(record.raw_website),
            "has_local_context": bool(record.raw_suburb or record.raw_city),
            "has_personalization_evidence": bool(record.evidence),
            "raw_quality_notes": "raw quality only; not lead score",
        }

    def build_source_run_summary(self, source_run: SourceRun) -> dict[str, object]:
        records = self.session.scalars(
            select(RawSourceRecord).where(RawSourceRecord.source_run_id == source_run.id)
        ).all()
        evidence = self.session.scalars(
            select(RawPersonalizationEvidence).where(
                RawPersonalizationEvidence.source_run_id == source_run.id
            )
        ).all()
        requests = self.session.scalars(
            select(SourceRequest).where(SourceRequest.source_run_id == source_run.id)
        ).all()
        evidence_counts = Counter(item.evidence_type for item in evidence)
        usable_context = [
            record.id
            for record in records
            if record.raw_name and (record.raw_category or record.raw_suburb or record.raw_city)
        ]
        risk_flags = [item.risk_flag for item in evidence if item.risk_flag]
        cache_hits = sum(1 for request in requests if request.cache_hit)
        return {
            "warning": RAW_ONLY_WARNING,
            "run_id": source_run.run_id,
            "status": source_run.status.value,
            "source_name": source_run.source_name.value,
            "total_records_fetched": source_run.fetched_count,
            "total_stored": source_run.stored_count,
            "total_skipped": source_run.skipped_count,
            "duplicate_fingerprint_count": source_run.skipped_count,
            "records_with_name": sum(1 for record in records if record.raw_name),
            "records_with_category": sum(1 for record in records if record.raw_category),
            "records_with_coordinates": sum(
                1 for record in records if record.raw_lat and record.raw_lng
            ),
            "records_with_address": sum(1 for record in records if record.raw_address),
            "records_with_phone": sum(1 for record in records if record.raw_phone),
            "records_with_raw_email": sum(1 for record in records if record.raw_email),
            "records_with_raw_website": sum(1 for record in records if record.raw_website),
            "records_missing_raw_website_field": sum(
                1 for record in records if not record.raw_website
            ),
            "records_with_social_contact_hints": sum(
                1 for record in records if record.raw_social_links_json
            ),
            "raw_personalization_evidence_count": len(evidence),
            "evidence_types_breakdown": dict(evidence_counts),
            "cache_hit_ratio": cache_hits / len(requests) if requests else 0,
            "errors": source_run.error_count,
            "budget_usage_estimate": source_run.metadata_json.get("credit_estimate", 0)
            if source_run.metadata_json
            else 0,
            "future_personalization": {
                "records_with_usable_business_name_category_suburb_evidence": len(usable_context),
                "records_with_insufficient_local_context": len(records) - len(usable_context),
                "records_with_risk_flags": len(set(risk_flags)),
                "records_where_website_missing_needs_verification": evidence_counts.get(
                    "website_field_missing", 0
                ),
                "records_with_contact_data_not_for_outreach": evidence_counts.get(
                    "email_present_raw", 0
                ),
            },
            "final_verdict": _final_verdict(source_run.status.value),
        }


def write_source_report(
    summary: dict[str, object], reports_dir: Path, prefix: str
) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(summary["run_id"])
    json_path = reports_dir / f"{prefix}-{run_id}.json"
    md_path = reports_dir / f"{prefix}-{run_id}.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        f"# {prefix.replace('-', ' ').title()}",
        "",
        str(summary["warning"]),
        "",
        f"- run_id: `{run_id}`",
        f"- status: `{summary['status']}`",
        f"- source_name: `{summary['source_name']}`",
        f"- total_stored: `{summary['total_stored']}`",
        f"- raw_personalization_evidence_count: `{summary['raw_personalization_evidence_count']}`",
        f"- final_verdict: `{summary['final_verdict']}`",
        "",
        "## Evidence Breakdown",
    ]
    breakdown = summary.get("evidence_types_breakdown", {})
    if isinstance(breakdown, dict):
        lines.extend(f"- {key}: {value}" for key, value in breakdown.items())
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def _final_verdict(status: str) -> str:
    if status == "COMPLETED":
        return "PHASE_2_RAW_SOURCE_CONNECTORS_READY"
    if status == "DRY_RUN_ONLY":
        return "PHASE_2_DRY_RUN_READY_WITH_LIVE_CONFIG_GAPS"
    if status == "BLOCKED_BY_SAFETY":
        return "SOURCE_RUN_BLOCKED_BY_SAFETY_EXPECTED"
    return status
